from langchain_core.retrievers import BaseRetriever
from rank_bm25 import BM25Okapi
from typing import List, Any, Union
from langchain.docstore.document import Document
from pydantic import PrivateAttr

class SparseRetriever(BaseRetriever):
    _corpus: List[Document] = PrivateAttr()
    _tokenized_corpus: List[List[str]] = PrivateAttr()
    _bm25: BM25Okapi = PrivateAttr()

    def __init__(self, corpus: List[Union[Document, str]]):
        super().__init__()
        # 支持传入 Document 或 str
        if isinstance(corpus[0], Document):
            self._corpus = corpus
            self._tokenized_corpus = [doc.page_content.split() for doc in corpus]
        else:
            self._corpus = [Document(page_content=text, metadata={}) for text in corpus]
            self._tokenized_corpus = [text.split() for text in corpus]
        self._bm25 = BM25Okapi(self._tokenized_corpus)

    def _get_relevant_documents(self, query: str) -> List[Document]:
        tokenized_query = query.split()
        scores = self._bm25.get_scores(tokenized_query)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:5]
        # 返回原始 Document，保留 metadata 并补充 bm25_score
        results = []
        for i in top_indices:
            doc = self._corpus[i]
            meta = dict(doc.metadata) if doc.metadata else {}
            meta["bm25_score"] = scores[i]
            results.append(Document(page_content=doc.page_content, metadata=meta))
        return results

    async def aget_relevant_documents(self, query: str) -> List[Document]:
        return self._get_relevant_documents(query) 