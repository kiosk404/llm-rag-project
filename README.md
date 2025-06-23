# RAG 项目功能总结

## 项目概述

这是一个基于 LangChain 的检索增强生成（RAG）应用，采用现代化的软件架构设计，支持多种大语言模型和文本分块策略。

## 核心功能

### 1. 多模型支持
- **通义千问 (Tongyi)**: 支持 qwen-turbo, qwen-plus, qwen-max 等模型
- **豆包 (Doubao)**: 支持 doubao-pro, doubao-lite 等模型  
- **Ollama 本地模型**: 支持 qwen2.5:7b, llama2:7b 等本地模型
- **嵌入模型**: 使用 nomic-embed-text:latest 进行向量化

### 2. 多种文本分块策略
实现了7种不同的文本分块策略，适应不同场景需求：

1. **固定大小分块**: 简单快速，按字符数分割
2. **重叠分块**: 保持上下文连贯性
3. **递归分块**: 智能识别自然边界（推荐）
4. **Token分块**: 基于LLM token分割
5. **Markdown分块**: 保持文档层次结构
6. **语义分块(spaCy)**: 高质量语义分割
7. **语义分块(NLTK)**: 轻量级语义分割

---

| 策略 | 处理速度 | 内存使用 | 分割质量 | 适用性 |
|------|----------|----------|----------|--------|
| 固定大小分块 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| 重叠分块 | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| 递归分块 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Token分块 | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| Markdown分块 | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| 语义分块(spaCy) | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 语义分块(NLTK) | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

### 推荐配置

- **通用场景**: 递归分块，chunk_size=500, chunk_overlap=50
- **精确检索**: 语义分块(spaCy)，chunk_size=500, chunk_overlap=100
- **快速处理**: 固定大小分块，chunk_size=1000, chunk_overlap=0
- **资源受限**: 语义分块(NLTK)，chunk_size=800, chunk_overlap=50


### 3. 交互式命令行界面
- 使用 questionary 提供友好的交互式体验
- 支持分块策略选择和参数配置
- 实时显示处理进度和结果

### 4. 向量数据库集成
- 基于 FAISS 的高效向量检索
- 支持向量库的创建、保存和加载
- 自动处理反序列化安全限制

## 项目结构

```
.
├── app/
│   ├── cli/                    # 命令行接口
│   │   ├── ingest.py          # 数据摄入命令
│   │   └── query.py           # 查询命令
│   ├── core/                  # 核心配置和异常
│   │   ├── config.py          # 配置文件
│   │   └── exceptions.py      # 自定义异常类
│   ├── models/                # 模型定义模块
│   │   ├── base.py            # 模型基类
│   │   ├── factory.py         # 模型工厂
│   │   ├── wrappers/          # 模型包装器
│   │   │   ├── __init__.py    # 包装器包初始化
│   │   │   └── robust_wrapper.py # 通用模型包装器
│   │   └── providers/         # 模型提供者
│   │       ├── tongyi.py      # 通义千问提供者
│   │       ├── doubao.py      # 豆包提供者
│   │       └── ollama.py      # Ollama提供者
│   └── services/              # 核心服务
│       ├── chunking_strategies.py  # 文本分块策略
│       ├── document_service.py    # 文档处理服务
│       ├── qa_service.py          # 问答服务
│       └── vector_store_service.py # 向量数据库服务
├── docs/                      # PDF 文档目录
├── examples/                  # 使用示例
│   ├── chunking_demo.py       # 分块策略演示
│   └── robust_wrapper_demo.py # 通用包装器演示
├── vector_store/              # 向量数据库存储
├── main.py                    # 主入口文件
└── requirements.txt           # 依赖文件
```

## 架构设计

### 模块化分层架构

1. **核心层 (Core)**: 配置管理和异常处理
2. **模型层 (Models)**: 模型定义、工厂模式和提供者实现
3. **服务层 (Services)**: 业务逻辑实现，包括分块策略
4. **接口层 (CLI)**: 用户交互界面

### 设计模式应用

- **工厂模式**: `LLMFactory` 统一管理模型创建，`ChunkingStrategyFactory` 管理分块策略
- **策略模式**: `LLMProvider` 抽象接口，`ChunkingStrategy` 抽象分块策略
- **装饰器模式**: `RobustLLMWrapper` 为模型提供统一的错误处理和重试机制
- **单例模式**: 服务类确保资源复用

## 通用模型包装器

项目提供了 `RobustLLMWrapper` 通用包装器，为所有模型提供者提供统一的错误处理和重试机制：

### 主要特性

- **统一错误处理**: 支持自定义错误模式，针对不同错误类型提供不同的处理策略
- **智能重试机制**: 可配置的重试次数和延迟，支持指数退避
- **错误分类**: 自动识别配额错误、网络错误、认证错误等
- **可扩展性**: 支持动态添加新的错误模式
- **多模型支持**: 可包装任何继承自 `BaseLLM` 的模型

### 使用示例

```python
from app.models.wrappers import create_robust_wrapper
from langchain_community.llms import Tongyi

# 创建基础模型
base_llm = Tongyi(model_name="qwen-turbo", api_key="your_key")

# 使用包装器包装
robust_llm = create_robust_wrapper(
    llm_instance=base_llm,
    provider_name="通义千问",
    max_retries=3,
    retry_delay=1,
    custom_error_patterns={
        "quota_error": {
            "keywords": ["quota", "balance", "欠费"],
            "message": "账户余额不足，请充值",
            "retry": False
        }
    }
)

# 使用包装后的模型
result = robust_llm.invoke("你好")
```

## 文本分块策略

项目支持7种不同的文本分块策略，每种策略适用于不同的场景：

### 1. 固定大小分块
- **描述**: 按照指定的字符数进行简单分割，不考虑语义边界
- **适用场景**: 需要严格控制块大小的场景
- **特点**: 简单快速，但可能破坏语义完整性

### 2. 重叠分块
- **描述**: 在固定大小分块基础上添加重叠区域，保持上下文连贯性
- **适用场景**: 需要保持上下文连贯性的场景
- **特点**: 避免信息丢失，但会增加存储开销

### 3. 递归分块
- **描述**: 智能识别段落、句子等自然边界，优先在语义完整处分割
- **适用场景**: 大多数文档的通用选择
- **特点**: 平衡了效率和语义完整性

### 4. Token分块
- **描述**: 基于语言模型的token进行分割，更适合LLM处理
- **适用场景**: 与LLM配合使用的场景
- **特点**: 更符合LLM的处理方式

### 5. Markdown分块
- **描述**: 优先按标题结构分割，保持文档层次结构
- **适用场景**: Markdown格式文档
- **特点**: 保持文档的层次结构信息

### 6. 语义分块(spaCy)
- **描述**: 使用spaCy进行语义分析，按句子和语义边界分割
- **适用场景**: 需要保持语义完整性的场景
- **特点**: 高质量的语义分割，需要安装spaCy

### 7. 语义分块(NLTK)
- **描述**: 使用NLTK进行句子分割，保持语义完整性
- **适用场景**: 需要保持语义完整性的场景
- **特点**: 轻量级的语义分割，需要安装NLTK

## 快速开始

### 1. 安装依赖

#### 方式一：使用安装脚本（推荐）

```bash
# 运行安装脚本
./install_dependencies.sh
```

脚本会自动：
- 检查Python版本
- 创建虚拟环境
- 安装所有依赖
- 下载可选的spaCy模型和NLTK数据
- 测试模块导入

#### 方式二：手动安装

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 安装spaCy模型（可选，用于语义分块）
python -m spacy download zh_core_web_sm  # 中文模型
python -m spacy download en_core_web_sm  # 英文模型

# 下载NLTK数据（可选，用于NLTK语义分块）
python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger')"
```

### 2. 配置环境变量

创建 `.env` 文件并配置以下内容：

```bash
# 通义千问 API 密钥
DASHSCOPE_API_KEY=your_dashscope_api_key_here

# 豆包 API 密钥（可选）
DOUBAO_API_KEY=your_doubao_api_key_here

# Ollama 服务地址（可选，默认 http://localhost:11434）
OLLAMA_BASE_URL=http://localhost:11434
```

### 3. 准备文档

将您的 PDF 文件放入 `docs/` 目录。

### 4. 数据摄入

```bash
python main.py ingest
```

程序会引导您选择：
- 文本分割策略（7种可选）
- 文本块大小
- 文本块重叠大小

### 5. 开始问答

```bash
python main.py query
```

输入您的问题，系统会基于您的文档进行回答。

### 6. 分块策略演示

```bash
python examples/chunking_demo.py
```

查看各种分块策略的效果和差异。

### 7. 提前下载 huggingface 的 reranker 模型

```bash
export HF_ENDPOINT=https://hf-mirror.com
huggingface-cli download BAAI/bge-reranker-v2-m3
```

## 支持的模型

### 1. 通义千问 (Tongyi)
- 模型：qwen-turbo, qwen-plus, qwen-max 等
- 配置：在 `app/core/config.py` 中设置 `LLM_PROVIDER = "tongyi"`

### 2. 豆包 (Doubao)
- 模型：doubao-pro, doubao-lite 等
- 配置：在 `app/core/config.py` 中设置 `LLM_PROVIDER = "doubao"`

### 3. Ollama 本地模型
- 模型：qwen2.5:7b, llama2:7b 等
- 配置：在 `app/core/config.py` 中设置 `LLM_PROVIDER = "ollama"`

## 高级用法

### 使用工厂模式创建模型

```python
from app.models import LLMFactory
from app.services.qa_service import QAService

# 创建通义千问提供者
tongyi_provider = LLMFactory.create_provider("tongyi", model_name="qwen-plus")

# 创建问答服务
qa_service = QAService(llm_provider=tongyi_provider)
```

### 注册自定义模型提供者

```python
from app.models import LLMFactory, LLMProvider

class CustomProvider(LLMProvider):
    def create_llm(self):
        # 实现自定义模型创建逻辑
        pass
    
    def get_provider_name(self):
        return "自定义提供者"

# 注册新的提供者
LLMFactory.register_provider("custom", CustomProvider)
```

### 查看所有可用提供者

```python
from app.models import LLMFactory

providers = LLMFactory.get_available_providers()
print(f"可用提供者: {providers}")
```

## 配置说明

### 模型配置 (`app/core/config.py`)

```python
# 模型提供者类型
LLM_PROVIDER = "tongyi"  # tongyi, doubao, ollama

# 模型名称
LLM_MODEL_NAME = "qwen-turbo"

# 嵌入模型
EMBEDDING_MODEL_NAME = "nomic-embed-text:latest"

# 文本分割配置
DEFAULT_CHUNK_SIZE = 256
DEFAULT_CHUNK_OVERLAP = 32
```

### 常见问题

1. **API 密钥错误**
   - 确保 `.env` 文件中的 API 密钥正确
   - 检查 API 密钥是否有效

2. **Ollama 连接失败**
   - 确保 Ollama 服务正在运行
   - 检查 `OLLAMA_BASE_URL` 配置

3. **向量库加载失败**
   - 确保已经运行过 `ingest` 命令
   - 检查向量库文件是否存在

4. **模块导入错误**
   - 确保使用 `PYTHONPATH=.` 运行示例
   - 检查项目结构是否正确

## 许可证

MIT License 