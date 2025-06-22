from langchain_core.retrievers import BaseRetriever
from typing import List, Any, Callable
from langchain.docstore.document import Document
from pydantic import PrivateAttr

class HybridRetriever(BaseRetriever):
    _dense_retriever: BaseRetriever = PrivateAttr()
    _sparse_retriever: BaseRetriever = PrivateAttr()
    _fusion_strategy: Callable = PrivateAttr()

    def __init__(self, dense_retriever: BaseRetriever, sparse_retriever: BaseRetriever, fusion_strategy: Callable):
        super().__init__()
        self._dense_retriever = dense_retriever
        self._sparse_retriever = sparse_retriever
        self._fusion_strategy = fusion_strategy

    def _get_relevant_documents(self, query: str) -> List[Document]:
        dense_results = self._dense_retriever._get_relevant_documents(query)
        sparse_results = self._sparse_retriever._get_relevant_documents(query)
        return self._fusion_strategy(dense_results, sparse_results)

    async def aget_relevant_documents(self, query: str) -> List[Document]:
        return self._get_relevant_documents(query) 