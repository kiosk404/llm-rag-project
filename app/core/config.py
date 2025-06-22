import os
from pathlib import Path

# 项目根目录，例如：BASE_DIR / 'subdir'
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 文档目录
DOCS_DIR = BASE_DIR / "docs"

# 向量数据库存储目录
VECTOR_STORE_DIR = BASE_DIR / "vector_store"
VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)

# FAISS 索引文件路径
FAISS_INDEX_PATH = str(VECTOR_STORE_DIR / "faiss_index")

# --- 模型配置 ---
# Ollama 服务地址
OLLAMA_BASE_URL = "http://localhost:11434"

# 嵌入模型 (Ollama)
EMBEDDING_MODEL_NAME = "nomic-embed-text:latest"

# 大语言模型配置
# 模型类型: tongyi, doubao, ollama
LLM_PROVIDER = "tongyi"

# 大语言模型名称 (根据提供者类型)
LLM_MODEL_NAME = "qwen-turbo"  # 通义千问
# LLM_MODEL_NAME = "doubao-pro"  # 豆包
# LLM_MODEL_NAME = "qwen2.5:7b"  # Ollama

# --- 文本块配置 ---
DEFAULT_CHUNK_SIZE = 256
DEFAULT_CHUNK_OVERLAP = 32 