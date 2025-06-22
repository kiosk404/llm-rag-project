import os
from typing import List, Optional

from langchain.docstore.document import Document
from langchain.embeddings.base import Embeddings
from langchain_community.vectorstores.faiss import FAISS

from app.core.config import FAISS_INDEX_PATH


def create_and_save_vector_store(chunks: List[Document], embeddings: Embeddings) -> FAISS:
    """
    从文档块创建 FAISS 向量库并保存到磁盘。
    参数：
        chunks (List[Document]): 文档块列表。
        embeddings (Embeddings): 使用的嵌入模型实例。
    返回：
        FAISS: 创建的 FAISS 向量库实例。
    """
    print("正在创建并保存向量库...")
    vector_store = FAISS.from_documents(chunks, embeddings)
    vector_store.save_local(FAISS_INDEX_PATH)
    print(f"向量库已保存到 {FAISS_INDEX_PATH}")
    return vector_store


def load_vector_store(embeddings: Embeddings) -> Optional[FAISS]:
    """
    从磁盘加载 FAISS 向量库。
    参数：
        embeddings (Embeddings): 使用的嵌入模型实例。
    返回：
        Optional[FAISS]: 加载的 FAISS 向量库实例，如果未找到则为 None。
    """
    if os.path.exists(FAISS_INDEX_PATH):
        print(f"正在从 {FAISS_INDEX_PATH} 加载向量库")
        return FAISS.load_local(
            FAISS_INDEX_PATH, 
            embeddings, 
            allow_dangerous_deserialization=True
        )
    else:
        print("未找到向量库。")
        return None 