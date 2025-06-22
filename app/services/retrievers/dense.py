from langchain_core.retrievers import BaseRetriever
from langchain_community.vectorstores.faiss import FAISS
from typing import List, Any
from langchain.docstore.document import Document
from pydantic import PrivateAttr

class DenseRetriever(BaseRetriever):
    _vector_store: FAISS = PrivateAttr()

    def __init__(self, vector_store: FAISS):
        super().__init__()
        self._vector_store = vector_store

    def _get_relevant_documents(self, query: str) -> List[Document]:
        # 兼容 langchain 检索器接口
        return self._vector_store.similarity_search(query)

    async def aget_relevant_documents(self, query: str) -> List[Document]:
        # 异步接口
        return self._get_relevant_documents(query) 