# 文本分块策略详解

本文档详细介绍了项目中实现的7种文本分块策略，每种策略的特点、适用场景和使用方法。

## 策略概览

| 策略名称 | 类型 | 特点 | 适用场景 |
|---------|------|------|----------|
| 固定大小分块 | 基础 | 简单快速，按字符数分割 | 需要严格控制块大小 |
| 重叠分块 | 基础 | 保持上下文连贯性 | 需要避免信息丢失 |
| 递归分块 | 智能 | 识别自然边界 | 大多数文档的通用选择 |
| Token分块 | 专业 | 基于LLM token | 与LLM配合使用 |
| Markdown分块 | 结构化 | 保持文档层次 | Markdown格式文档 |
| 语义分块(spaCy) | 语义 | 高质量语义分割 | 需要语义完整性 |
| 语义分块(NLTK) | 语义 | 轻量级语义分割 | 需要语义完整性 |

## 详细说明

### 1. 固定大小分块

**实现原理**: 使用 `CharacterTextSplitter`，按照指定的字符数进行简单分割。

**特点**:
- ✅ 简单快速
- ✅ 可预测的块大小
- ❌ 可能破坏语义完整性
- ❌ 不考虑自然边界

**适用场景**:
- 需要严格控制块大小的场景
- 对处理速度要求高的场景
- 文档结构相对简单的场景

**参数建议**:
- `chunk_size`: 500-1000
- `chunk_overlap`: 0-50

### 2. 重叠分块

**实现原理**: 在固定大小分块基础上添加重叠区域。

**特点**:
- ✅ 保持上下文连贯性
- ✅ 避免信息丢失
- ✅ 提高检索准确性
- ❌ 增加存储开销
- ❌ 可能产生冗余

**适用场景**:
- 需要保持上下文连贯性的场景
- 对检索准确性要求高的场景
- 文档内容关联性强的场景

**参数建议**:
- `chunk_size`: 500-1000
- `chunk_overlap`: 50-200

### 3. 递归分块

**实现原理**: 使用 `RecursiveCharacterTextSplitter`，智能识别段落、句子等自然边界。

**特点**:
- ✅ 智能识别自然边界
- ✅ 平衡效率和语义完整性
- ✅ 适合大多数文档
- ✅ 支持自定义分隔符

**适用场景**:
- 大多数文档的通用选择
- 需要平衡效率和质量的场景
- 文档结构复杂的场景

**参数建议**:
- `chunk_size`: 500-1000
- `chunk_overlap`: 50-100

### 4. Token分块

**实现原理**: 使用 `TokenTextSplitter`，基于语言模型的token进行分割。

**特点**:
- ✅ 更符合LLM的处理方式
- ✅ 基于语义单位分割
- ✅ 适合与LLM配合使用
- ❌ 需要额外的tokenizer
- ❌ 处理速度相对较慢

**适用场景**:
- 与LLM配合使用的场景
- 需要精确控制token数量的场景
- 对语义理解要求高的场景

**参数建议**:
- `chunk_size`: 100-500 (token数)
- `chunk_overlap`: 20-100 (token数)

### 5. Markdown分块

**实现原理**: 先按Markdown标题分割，再对每个部分进行递归分割。

**特点**:
- ✅ 保持文档层次结构
- ✅ 按逻辑章节分割
- ✅ 适合结构化文档
- ❌ 仅适用于Markdown格式
- ❌ 需要文档有清晰的标题结构

**适用场景**:
- Markdown格式文档
- 有清晰章节结构的文档
- 需要保持文档逻辑结构的场景

**参数建议**:
- `chunk_size`: 500-1000
- `chunk_overlap`: 50-100

### 6. 语义分块(spaCy)

**实现原理**: 使用spaCy进行语义分析，按句子和语义边界分割。

**特点**:
- ✅ 高质量的语义分割
- ✅ 基于语言学分析
- ✅ 支持多种语言
- ❌ 需要安装spaCy模型
- ❌ 处理速度较慢
- ❌ 资源消耗较大

**适用场景**:
- 需要保持语义完整性的场景
- 对分割质量要求极高的场景
- 多语言文档处理

**参数建议**:
- `chunk_size`: 500-1000
- `chunk_overlap`: 50-100

### 7. 语义分块(NLTK)

**实现原理**: 使用NLTK进行句子分割，保持语义完整性。

**特点**:
- ✅ 轻量级的语义分割
- ✅ 基于句子边界
- ✅ 资源消耗较小
- ❌ 需要下载NLTK数据
- ❌ 语义分析能力有限

**适用场景**:
- 需要保持语义完整性的场景
- 资源受限的环境
- 英文文档处理

**参数建议**:
- `chunk_size`: 500-1000
- `chunk_overlap`: 50-100

## 选择建议

### 按文档类型选择

| 文档类型 | 推荐策略 | 备选策略 |
|---------|----------|----------|
| 技术文档 | 递归分块 | 重叠分块 |
| 学术论文 | 递归分块 | 语义分块(spaCy) |
| 新闻文章 | 语义分块(NLTK) | 递归分块 |
| Markdown文档 | Markdown分块 | 递归分块 |
| 代码文档 | 固定大小分块 | 递归分块 |
| 多语言文档 | 语义分块(spaCy) | 递归分块 |

### 按性能要求选择

| 性能要求 | 推荐策略 | 备选策略 |
|---------|----------|----------|
| 速度优先 | 固定大小分块 | 重叠分块 |
| 质量优先 | 语义分块(spaCy) | 递归分块 |
| 平衡型 | 递归分块 | 语义分块(NLTK) |
| 资源受限 | 语义分块(NLTK) | 固定大小分块 |

### 按应用场景选择

| 应用场景 | 推荐策略 | 备选策略 |
|---------|----------|----------|
| 通用RAG | 递归分块 | 重叠分块 |
| 精确问答 | 语义分块(spaCy) | 递归分块 |
| 文档摘要 | 语义分块(NLTK) | 递归分块 |
| 代码分析 | 固定大小分块 | Token分块 |
| 多语言处理 | 语义分块(spaCy) | 递归分块 |

## 使用示例

### 命令行使用

```bash
# 运行数据摄入，选择分块策略
python main.py ingest

# 运行分块策略演示
python examples/chunking_demo.py
```

### 编程使用

```python
from app.services.chunking_strategies import ChunkingStrategyFactory
from app.services.document_service import load_documents

# 加载文档
documents = load_documents()

# 选择分块策略
strategy = ChunkingStrategyFactory.get_strategy("递归分块")

# 执行分块
chunks = strategy.split_documents(
    documents,
    chunk_size=500,
    chunk_overlap=50
)

print(f"创建了 {len(chunks)} 个文本块")
```

### 参数调优

```python
# 不同场景的参数建议
scenarios = {
    "快速处理": {"chunk_size": 1000, "chunk_overlap": 0},
    "精确检索": {"chunk_size": 500, "chunk_overlap": 100},
    "语义保持": {"chunk_size": 800, "chunk_overlap": 150},
    "资源优化": {"chunk_size": 1200, "chunk_overlap": 50}
}
```

## 性能对比

| 策略 | 处理速度 | 内存使用 | 分割质量 | 适用性 |
|------|----------|----------|----------|--------|
| 固定大小分块 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| 重叠分块 | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| 递归分块 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Token分块 | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| Markdown分块 | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| 语义分块(spaCy) | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 语义分块(NLTK) | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

## 故障排除

### 常见问题

1. **Token分块失败**
   - 解决方案: 安装tiktoken包 `pip install tiktoken`

2. **spaCy模型加载失败**
   - 解决方案: 下载spaCy模型 `python -m spacy download zh_core_web_sm`

3. **NLTK数据缺失**
   - 解决方案: 下载NLTK数据 `python -c "import nltk; nltk.download('punkt')"`

4. **分块结果不理想**
   - 调整chunk_size和chunk_overlap参数
   - 尝试不同的分块策略
   - 检查文档格式和质量

### 性能优化

1. **提高处理速度**
   - 使用固定大小分块或重叠分块
   - 增加chunk_size减少块数量
   - 减少chunk_overlap

2. **提高分割质量**
   - 使用语义分块策略
   - 调整chunk_size到合适大小
   - 增加chunk_overlap

3. **减少内存使用**
   - 使用轻量级策略如NLTK语义分块
   - 减少chunk_overlap
   - 分批处理大文档

## 扩展开发

### 添加新的分块策略

```python
from app.services.chunking_strategies import ChunkingStrategy

class CustomChunking(ChunkingStrategy):
    def split_documents(self, documents, **kwargs):
        # 实现自定义分块逻辑
        pass
    
    def get_description(self):
        return "自定义分块策略描述"

# 注册新策略
ChunkingStrategyFactory._strategies["自定义分块"] = CustomChunking
```

### 自定义分隔符

```python
# 在递归分块中使用自定义分隔符
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""]
)
```

## 总结

选择合适的文本分块策略是RAG系统成功的关键因素之一。建议：

1. **从递归分块开始**: 适合大多数场景，平衡了效率和质量
2. **根据文档特点调整**: 技术文档、学术论文、新闻文章等需要不同的策略
3. **考虑性能要求**: 速度、质量、资源消耗需要权衡
4. **实验和调优**: 通过实际测试找到最适合的参数组合
5. **持续优化**: 根据使用效果不断调整和改进

通过合理选择和使用这些分块策略，可以显著提高RAG系统的检索准确性和用户体验。 