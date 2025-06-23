from .base import BaseReranker
from typing import List, Any
from FlagEmbedding import FlagReranker
import transformers

transformers.logging.set_verbosity_error()

class LocalBGEReranker(BaseReranker):
    """
    本地 BGE 重排序器（基于 FlagEmbedding 实现，兼容 HuggingFace 格式模型）。
    用于对召回的文档块进行 query-passage 语义相关性重排序。
    支持 GPU/CPU，推理速度快，适合高性能 RAG 场景。
    默认加载 BAAI/bge-reranker-v2-m3，可自定义模型路径。
    """
    def __init__(self, model_name: str = "BAAI/bge-reranker-v2-m3", use_fp16: bool = True):
        """
        初始化本地 BGE 重排序器。
        :param model_name: HuggingFace Hub 模型名或本地路径
        :param use_fp16: 是否使用半精度（推荐 GPU 环境开启）
        """
        self.reranker = FlagReranker(model_name, use_fp16=use_fp16)

    def rerank(self, query: str, docs: List[Any], top_k: int = 5) -> List[Any]:
        """
        对召回的文档块进行重排序，返回相关性最高的 top_k 个文档。
        :param query: 用户查询
        :param docs: 召回的文档列表（需有 page_content 属性）
        :param top_k: 返回的文档数
        :return: 重排序后的文档列表
        """
        if not docs:
            return []
        # 构造 query-passage 输入对
        input_pairs = [[query, doc.page_content] for doc in docs]
        # 计算相关性分数
        scores = self.reranker.compute_score(input_pairs, normalize=True)
        # 按分数排序，返回 top_k
        sorted_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        reranking_docs = [docs[i] for i in sorted_indices[:top_k]]
        return reranking_docs 