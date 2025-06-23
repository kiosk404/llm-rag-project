"""问答服务模块"""

import time
from typing import Optional, Dict, Any, List
from langchain.chains import RetrievalQA
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores.faiss import FAISS
from langchain_core.language_models import BaseLLM
from dotenv import load_dotenv

from app.core.config import EMBEDDING_MODEL_NAME, LLM_MODEL_NAME, LLM_PROVIDER, OLLAMA_BASE_URL
from app.models import LLMProvider, LLMFactory
from app.core.exceptions import ServiceError, ConfigurationError
from app.services.retrievers.dense import DenseRetriever
from app.services.retrievers.sparse import SparseRetriever
from app.services.retrievers.hybrid import HybridRetriever
from app.services.fusion import simple_fusion
from app.services.document_service import load_documents
from app.services.rerankers.local_bge_reranker import LocalBGEReranker

load_dotenv()


class QAService:
    """问答服务类"""
    
    def __init__(self, llm_provider: LLMProvider = None, reranker: Any = None, use_rerank: bool = False):
        """
        初始化问答服务
        
        参数：
            llm_provider: 大语言模型提供者，如果为 None 则使用配置文件中的默认设置
            reranker: 重排序器，如果为 None 则不使用重排序
            use_rerank: 是否使用重排序
        """
        self.llm_provider = llm_provider or self._create_default_provider()
        self.embedding_model = None
        self.qa_chain = None
        self.max_retries = 1
        self.retry_delay = 2  # 秒
        self.reranker = reranker
        self.use_rerank = use_rerank
    
    def _create_default_provider(self) -> LLMProvider:
        """创建默认的模型提供者"""
        try:
            return LLMFactory.create_provider(LLM_PROVIDER, model_name=LLM_MODEL_NAME)
        except Exception as e:
            raise ServiceError(
                f"创建模型提供者失败：{e}\n"
                f"请检查配置文件中的 LLM_PROVIDER 和 LLM_MODEL_NAME 设置。"
            )
    
    def load_embedding_model(self) -> OllamaEmbeddings:
        """
        加载嵌入模型
        返回：
            OllamaEmbeddings: 加载的嵌入模型实例
        """
        if self.embedding_model is None:
            try:
                print(f"正在从 Ollama 加载嵌入模型: {EMBEDDING_MODEL_NAME}")
                self.embedding_model = OllamaEmbeddings(
                    model=EMBEDDING_MODEL_NAME, 
                    base_url=OLLAMA_BASE_URL
                )
                # 测试嵌入模型
                test_embedding = self.embedding_model.embed_query("测试")
            except Exception as e:
                raise ServiceError(
                    f"加载嵌入模型失败：{e}\n"
                    f"请确保 Ollama 服务正在运行，"
                    f"并且模型 {EMBEDDING_MODEL_NAME} 已安装。"
                )
        return self.embedding_model
    
    def load_llm(self) -> BaseLLM:
        """
        加载大语言模型
        返回：
            BaseLLM: 加载的大语言模型实例
        """
        try:
            print(f"正在加载 {self.llm_provider.get_provider_name()} 模型...")
            llm = self.llm_provider.create_llm()
            
            return llm
        except Exception as e:
            raise ServiceError(
                f"加载大语言模型失败：{e}\n"
                f"请检查API密钥配置和网络连接。"
            )
    
    def create_retriever(self, vector_store: FAISS, retrieval_mode: str = 'dense', corpus: list = None):
        """
        创建检索器，支持 dense/sparse/hybrid
        参数：
            vector_store: FAISS 向量库实例
            retrieval_mode: 检索模式（dense/sparse/hybrid）
            corpus: 稀疏检索语料（list of Document）
        返回：
            检索器实例
        """
        if retrieval_mode == 'dense':
            return DenseRetriever(vector_store)
        elif retrieval_mode == 'sparse':
            if corpus is None:
                documents = load_documents()
                corpus = documents  # 直接传递 Document 对象
            return SparseRetriever(corpus)
        elif retrieval_mode == 'hybrid':
            if corpus is None:
                documents = load_documents()
                corpus = documents
            dense = DenseRetriever(vector_store)
            sparse = SparseRetriever(corpus)
            return HybridRetriever(dense, sparse, simple_fusion)
        else:
            raise ValueError(f"未知检索模式: {retrieval_mode}")

    def create_qa_chain(self, vector_store: FAISS, retrieval_mode: str = 'dense', corpus: list = None) -> RetrievalQA:
        """
        创建问答链，支持混合检索
        参数：
            vector_store: FAISS 向量库实例
            retrieval_mode: 检索模式（dense/sparse/hybrid）
            corpus: 稀疏检索语料
        返回：
            RetrievalQA: 创建的问答链
        """
        if self.qa_chain is None:
            try:
                llm = self.load_llm()
                retriever = self.create_retriever(vector_store, retrieval_mode, corpus)
                # 包装 retriever，支持 rerank
                if self.use_rerank and self.reranker is not None:
                    orig_get_relevant_documents = retriever._get_relevant_documents
                    def rerank_wrapper(query):
                        docs = orig_get_relevant_documents(query)
                        return self.reranker.rerank(query, docs)
                    retriever._get_relevant_documents = rerank_wrapper
                self.qa_chain = RetrievalQA.from_chain_type(
                    llm=llm,
                    chain_type="stuff",
                    retriever=retriever,
                    return_source_documents=True,
                )
            except Exception as e:
                raise ServiceError(
                    f"创建问答链失败：{e}\n"
                    f"请检查模型配置和向量库状态。"
                )
        return self.qa_chain
    
    def ask_question(self, query: str) -> Dict[str, Any]:
        """
        使用问答链进行提问，包含重试机制
        参数：
            query: 用户输入的问题
        返回：
            dict: 问答链的结果，包括答案和来源文档
        """
        if self.qa_chain is None:
            raise ServiceError("问答链尚未初始化，请先调用 create_qa_chain")
        
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                result = self.qa_chain.invoke({"query": query})
                
                # 检查结果是否有效
                if not result or not result.get("result"):
                    raise ServiceError("模型返回了空结果，请重试")
                
                return result
                
            except Exception as e:
                last_error = e
                error_msg = str(e).lower()
                
                # 检查是否是特定类型的错误
                if any(keyword in error_msg for keyword in [
                    "quota", "limit", "balance", "credit", "欠费", "余额不足"
                ]):
                    raise ServiceError(
                        f"模型调用失败：账户余额不足或配额超限。\n"
                        f"请检查您的账户余额或联系客服。\n"
                        f"错误详情：{e}"
                    )
                elif any(keyword in error_msg for keyword in [
                    "timeout", "connection", "network", "网络", "连接"
                ]):
                    if attempt < self.max_retries - 1:
                        print(f"网络连接错误，正在重试 ({attempt + 1}/{self.max_retries})...")
                        time.sleep(self.retry_delay * (attempt + 1))
                        continue
                    else:
                        raise ServiceError(
                            f"网络连接失败，已重试 {self.max_retries} 次。\n"
                            f"请检查网络连接或稍后重试。\n"
                            f"错误详情：{e}"
                        )
                elif any(keyword in error_msg for keyword in [
                    "invalid", "auth", "unauthorized", "认证", "授权"
                ]):
                    raise ServiceError(
                        f"API认证失败：请检查您的API密钥是否正确。\n"
                        f"错误详情：{e}"
                    )
                else:
                    # 其他未知错误
                    if attempt < self.max_retries - 1:
                        print(f"调用失败，正在重试 ({attempt + 1}/{self.max_retries})...")
                        time.sleep(self.retry_delay * (attempt + 1))
                        continue
                    else:
                        raise ServiceError(
                            f"模型调用失败，已重试 {self.max_retries} 次：{e}\n"
                            f"请稍后重试或联系技术支持。"
                        )
        
        # 如果所有重试都失败了
        raise ServiceError(f"模型调用失败，已重试 {self.max_retries} 次：{last_error}")


# 为了保持向后兼容性，提供原有的函数接口
def load_embedding_model() -> OllamaEmbeddings:
    """加载嵌入模型（向后兼容接口）"""
    service = QAService()
    return service.load_embedding_model()


def load_llm() -> BaseLLM:
    """加载大语言模型（向后兼容接口）"""
    service = QAService()
    return service.load_llm()


def create_qa_chain(vector_store: FAISS, retrieval_mode: str = 'dense', corpus: list = None, use_rerank: bool = False) -> RetrievalQA:
    """
    创建问答链（向后兼容接口）
    
    参数：
        vector_store: FAISS 向量库实例
        retrieval_mode: 检索模式（dense/sparse/hybrid）
        corpus: 稀疏检索语料
        use_rerank: 是否启用重排序
    返回：
        RetrievalQA: 创建的问答链
    """
    reranker = LocalBGEReranker() if use_rerank else None
    service = QAService(reranker=reranker, use_rerank=use_rerank)
    return service.create_qa_chain(vector_store, retrieval_mode, corpus)


def ask_question(chain: RetrievalQA, query: str) -> Dict[str, Any]:
    """使用问答链进行提问（向后兼容接口）"""
    return chain.invoke({"query": query}) 