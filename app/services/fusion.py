from typing import List
from collections import Counter
from langchain.docstore.document import Document

def simple_fusion(dense_results: List[Document], sparse_results: List[Document], top_k: int = 5) -> List[Document]:
    """
    融合稠密检索和稀疏检索的结果，返回去重后的前 top_k 个文档。

    参数：
        dense_results (List[Document]): 稠密检索（向量检索）返回的文档列表。
        sparse_results (List[Document]): 稀疏检索（BM25/关键词检索）返回的文档列表。
        top_k (int): 最终返回的文档数量。

    融合逻辑：
        1. 将两种检索结果合并。
        2. 以 page_content 作为唯一标识去重。
        3. 统计每个文档在合并结果中出现的次数。
        4. 按出现频次降序排序，频次高的排前面。
        5. 返回排序后的前 top_k 个文档。

    返回：
        List[Document]: 融合、去重、排序后的文档列表。
    """
    all_results = dense_results + sparse_results
    counter = Counter([doc.page_content for doc in all_results])
    unique_docs = {}
    for doc in all_results:
        key = doc.page_content
        if key not in unique_docs:
            unique_docs[key] = doc
    sorted_docs = sorted(unique_docs.values(), key=lambda d: counter[d.page_content], reverse=True)
    return sorted_docs[:top_k] 