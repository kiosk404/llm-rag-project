from typing import List, Type
from langchain.docstore.document import Document
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import TextSplitter, RecursiveCharacterTextSplitter

from app.core.config import DOCS_DIR
from app.services.chunking_strategies import (
    ChunkingStrategyFactory,
    split_documents_with_strategy
)


def load_documents() -> List[Document]:
    """
    从配置的文档目录加载所有 PDF 文档。

    返回：
        List[Document]: 加载后的文档列表。
    """
    loader = PyPDFDirectoryLoader(str(DOCS_DIR))
    return loader.load()


def split_documents(
    documents: List[Document],
    splitter_class: Type[TextSplitter] = RecursiveCharacterTextSplitter,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> List[Document]:
    """
    使用指定的文本分割器将文档切分为更小的块。

    参数：
        documents (List[Document]): 需要切分的文档。
        splitter_class (Type[TextSplitter]): 文本分割器的类。
        chunk_size (int): 每个块的大小。
        chunk_overlap (int): 块之间的重叠。

    返回：
        List[Document]: 切分后的文档块列表。
    """
    text_splitter = splitter_class(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return text_splitter.split_documents(documents)


def split_documents_with_strategy_name(
    documents: List[Document],
    strategy_name: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> List[Document]:
    """
    使用指定的分块策略名称将文档切分为更小的块。

    参数：
        documents (List[Document]): 需要切分的文档。
        strategy_name (str): 分块策略名称。
        chunk_size (int): 每个块的大小。
        chunk_overlap (int): 块之间的重叠。

    返回：
        List[Document]: 切分后的文档块列表。
    """
    return split_documents_with_strategy(
        documents=documents,
        strategy_name=strategy_name,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )


def get_available_chunking_strategies() -> dict:
    """
    获取所有可用的分块策略及其描述。

    返回：
        dict: 策略名称到描述的映射。
    """
    return ChunkingStrategyFactory.get_available_strategies()


def get_chunking_strategy_names() -> List[str]:
    """
    获取所有可用的分块策略名称。

    返回：
        List[str]: 策略名称列表。
    """
    return ChunkingStrategyFactory.get_strategy_names() 