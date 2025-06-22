"""
文本分块策略模块

提供多种文本分块策略，包括：
- 固定大小分块
- 重叠分块  
- 递归分块
- 语义分块（基于spaCy和NLTK）
"""

from typing import List, Type, Optional, Dict, Any
from abc import ABC, abstractmethod
from langchain.docstore.document import Document
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    CharacterTextSplitter,
    TokenTextSplitter,
    MarkdownHeaderTextSplitter,
    HTMLHeaderTextSplitter,
)
from langchain.text_splitter import Language
import re


class ChunkingStrategy(ABC):
    """文本分块策略基类"""
    
    @abstractmethod
    def split_documents(self, documents: List[Document], **kwargs) -> List[Document]:
        """分割文档"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """获取策略描述"""
        pass


class FixedSizeChunking(ChunkingStrategy):
    """固定大小分块策略"""
    
    def split_documents(self, documents: List[Document], **kwargs) -> List[Document]:
        chunk_size = kwargs.get('chunk_size', 500)
        chunk_overlap = kwargs.get('chunk_overlap', 0)
        
        text_splitter = CharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separator="\n"
        )
        return text_splitter.split_documents(documents)
    
    def get_description(self) -> str:
        return "固定大小分块：按照指定的字符数进行简单分割，不考虑语义边界"


class OverlappingChunking(ChunkingStrategy):
    """重叠分块策略"""
    
    def split_documents(self, documents: List[Document], **kwargs) -> List[Document]:
        chunk_size = kwargs.get('chunk_size', 500)
        chunk_overlap = kwargs.get('chunk_overlap', 50)
        
        text_splitter = CharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separator="\n"
        )
        return text_splitter.split_documents(documents)
    
    def get_description(self) -> str:
        return "重叠分块：在固定大小分块基础上添加重叠区域，保持上下文连贯性"


class RecursiveChunking(ChunkingStrategy):
    """递归分块策略"""
    
    def split_documents(self, documents: List[Document], **kwargs) -> List[Document]:
        chunk_size = kwargs.get('chunk_size', 500)
        chunk_overlap = kwargs.get('chunk_overlap', 50)
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", "。", "！", "？", " ", ""]
        )
        return text_splitter.split_documents(documents)
    
    def get_description(self) -> str:
        return "递归分块：智能识别段落、句子等自然边界，优先在语义完整处分割"


class TokenBasedChunking(ChunkingStrategy):
    """基于Token的分块策略"""
    
    def split_documents(self, documents: List[Document], **kwargs) -> List[Document]:
        chunk_size = kwargs.get('chunk_size', 100)
        chunk_overlap = kwargs.get('chunk_overlap', 20)
        
        text_splitter = TokenTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        return text_splitter.split_documents(documents)
    
    def get_description(self) -> str:
        return "Token分块：基于语言模型的token进行分割，更适合LLM处理"


class MarkdownChunking(ChunkingStrategy):
    """Markdown文档分块策略"""
    
    def split_documents(self, documents: List[Document], **kwargs) -> List[Document]:
        chunk_size = kwargs.get('chunk_size', 500)
        chunk_overlap = kwargs.get('chunk_overlap', 50)
        
        # 先按Markdown标题分割
        headers_to_split_on = [
            ("#", "标题1"),
            ("##", "标题2"),
            ("###", "标题3"),
            ("####", "标题4"),
        ]
        
        markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split_on
        )
        
        # 然后对每个部分进行递归分割
        recursive_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", "。", "！", "？", " ", ""]
        )
        
        all_chunks = []
        for doc in documents:
            # 先按标题分割
            header_splits = markdown_splitter.split_text(doc.page_content)
            # 再递归分割
            for split in header_splits:
                chunks = recursive_splitter.split_text(split.page_content)
                for chunk in chunks:
                    all_chunks.append(Document(
                        page_content=chunk,
                        metadata=doc.metadata
                    ))
        
        return all_chunks
    
    def get_description(self) -> str:
        return "Markdown分块：优先按标题结构分割，保持文档层次结构"


class SemanticChunking(ChunkingStrategy):
    """语义分块策略（基于spaCy）"""
    
    def __init__(self):
        self.spacy_model = None
        # 不在初始化时加载模型，改为延迟加载
    
    def _load_spacy(self):
        """加载spaCy模型"""
        if self.spacy_model is not None:
            return
            
        try:
            import spacy
            # 尝试加载中文模型，如果没有则使用英文模型
            try:
                self.spacy_model = spacy.load("zh_core_web_sm")
            except OSError:
                try:
                    self.spacy_model = spacy.load("en_core_web_sm")
                except OSError:
                    # 如果都没有，使用默认模型
                    try:
                        self.spacy_model = spacy.load("xx_ent_wiki_sm")
                    except OSError:
                        # 如果所有模型都不可用，设置为None
                        self.spacy_model = None
        except ImportError:
            self.spacy_model = None
    
    def split_documents(self, documents: List[Document], **kwargs) -> List[Document]:
        # 延迟加载spaCy模型
        self._load_spacy()
        
        if not self.spacy_model:
            # 如果spaCy不可用，回退到递归分块
            fallback = RecursiveChunking()
            return fallback.split_documents(documents, **kwargs)
        
        chunk_size = kwargs.get('chunk_size', 500)
        chunk_overlap = kwargs.get('chunk_overlap', 50)
        
        all_chunks = []
        
        for doc in documents:
            # 使用spaCy进行语义分析
            spacy_doc = self.spacy_model(doc.page_content)
            
            # 按句子分割
            sentences = [sent.text.strip() for sent in spacy_doc.sents if sent.text.strip()]
            
            current_chunk = ""
            chunks = []
            
            for sentence in sentences:
                if len(current_chunk) + len(sentence) <= chunk_size:
                    current_chunk += sentence + " "
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence + " "
            
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            # 创建Document对象
            for chunk in chunks:
                all_chunks.append(Document(
                    page_content=chunk,
                    metadata=doc.metadata
                ))
        
        return all_chunks
    
    def get_description(self) -> str:
        return "语义分块：使用spaCy进行语义分析，按句子和语义边界分割"


class NLTKSemanticChunking(ChunkingStrategy):
    """基于NLTK的语义分块策略"""
    
    def __init__(self):
        self.nltk_available = False
        # 不在初始化时设置NLTK，改为延迟加载
    
    def _setup_nltk(self):
        """设置NLTK"""
        if self.nltk_available:
            return
            
        try:
            import nltk
            # 下载必要的NLTK数据
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                nltk.download('punkt')
            
            try:
                nltk.data.find('tokenizers/average_perceptron_tagger')
            except LookupError:
                nltk.download('averaged_perceptron_tagger')
            
            self.nltk_available = True
        except ImportError:
            self.nltk_available = False
    
    def split_documents(self, documents: List[Document], **kwargs) -> List[Document]:
        # 延迟设置NLTK
        self._setup_nltk()
        
        if not self.nltk_available:
            # 如果NLTK不可用，回退到递归分块
            fallback = RecursiveChunking()
            return fallback.split_documents(documents, **kwargs)
        
        import nltk
        from nltk.tokenize import sent_tokenize
        
        chunk_size = kwargs.get('chunk_size', 500)
        chunk_overlap = kwargs.get('chunk_overlap', 50)
        
        all_chunks = []
        
        for doc in documents:
            # 使用NLTK进行句子分割
            sentences = sent_tokenize(doc.page_content)
            
            current_chunk = ""
            chunks = []
            
            for sentence in sentences:
                if len(current_chunk) + len(sentence) <= chunk_size:
                    current_chunk += sentence + " "
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence + " "
            
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            # 创建Document对象
            for chunk in chunks:
                all_chunks.append(Document(
                    page_content=chunk,
                    metadata=doc.metadata
                ))
        
        return all_chunks
    
    def get_description(self) -> str:
        return "NLTK语义分块：使用NLTK进行句子分割，保持语义完整性"


class ChunkingStrategyFactory:
    """分块策略工厂类"""
    
    _strategies = {
        "固定大小分块": FixedSizeChunking,
        "重叠分块": OverlappingChunking,
        "递归分块": RecursiveChunking,
        "Token分块": TokenBasedChunking,
        "Markdown分块": MarkdownChunking,
        "语义分块(spaCy)": SemanticChunking,
        "语义分块(NLTK)": NLTKSemanticChunking,
    }
    
    @classmethod
    def get_strategy(cls, strategy_name: str) -> ChunkingStrategy:
        """获取指定的分块策略"""
        if strategy_name not in cls._strategies:
            raise ValueError(f"未知的分块策略: {strategy_name}")
        
        strategy_class = cls._strategies[strategy_name]
        return strategy_class()
    
    @classmethod
    def get_available_strategies(cls) -> Dict[str, str]:
        """获取所有可用的分块策略及其描述"""
        strategies = {}
        for name, strategy_class in cls._strategies.items():
            strategy = strategy_class()
            strategies[name] = strategy.get_description()
        return strategies
    
    @classmethod
    def get_strategy_names(cls) -> List[str]:
        """获取所有策略名称"""
        return list(cls._strategies.keys())


def split_documents_with_strategy(
    documents: List[Document],
    strategy_name: str,
    **kwargs
) -> List[Document]:
    """
    使用指定的分块策略分割文档
    
    参数：
        documents: 要分割的文档列表
        strategy_name: 分块策略名称
        **kwargs: 传递给分块策略的参数
    
    返回：
        分割后的文档块列表
    """
    strategy = ChunkingStrategyFactory.get_strategy(strategy_name)
    return strategy.split_documents(documents, **kwargs) 