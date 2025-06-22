#!/bin/bash

# RAG 项目依赖安装脚本

echo "🚀 开始安装 RAG 项目依赖..."

# 检查 Python 版本
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
if [[ $(echo "$python_version >= 3.8" | bc -l) -eq 0 ]]; then
    echo "❌ 需要 Python 3.8 或更高版本，当前版本: $python_version"
    exit 1
fi

echo "✅ Python 版本检查通过: $python_version"

# 创建虚拟环境
if [ ! -d ".venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv .venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source .venv/bin/activate

# 升级 pip
echo "⬆️ 升级 pip..."
pip install --upgrade pip

# 安装基础依赖
echo "📚 安装基础依赖..."
pip install -r requirements.txt

# 安装 spaCy 模型（可选）
echo "🤖 安装 spaCy 模型..."
echo "是否安装 spaCy 模型？(y/n)"
read -r install_spacy
if [[ $install_spacy =~ ^[Yy]$ ]]; then
    echo "📥 下载中文模型..."
    python -m spacy download zh_core_web_sm || echo "⚠️ 中文模型下载失败，将使用英文模型"
    echo "📥 下载英文模型..."
    python -m spacy download en_core_web_sm || echo "⚠️ 英文模型下载失败"
    echo "📥 下载通用模型..."
    python -m spacy download xx_ent_wiki_sm || echo "⚠️ 通用模型下载失败"
fi

# 下载 NLTK 数据（可选）
echo "📚 下载 NLTK 数据..."
echo "是否下载 NLTK 数据？(y/n)"
read -r install_nltk
if [[ $install_nltk =~ ^[Yy]$ ]]; then
    echo "📥 下载 NLTK 数据..."
    python -c "
import nltk
try:
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    print('✅ NLTK 数据下载成功')
except Exception as e:
    print(f'⚠️ NLTK 数据下载失败: {e}')
"
fi

# 测试导入
echo "🧪 测试模块导入..."
python -c "
try:
    from app.services.chunking_strategies import ChunkingStrategyFactory
    strategies = ChunkingStrategyFactory.get_available_strategies()
    print(f'✅ 成功导入分块策略模块，可用策略数量: {len(strategies)}')
    for name in strategies.keys():
        print(f'  - {name}')
except Exception as e:
    print(f'❌ 模块导入失败: {e}')
"

echo ""
echo "🎉 安装完成！"
echo ""
echo "📋 下一步操作："
echo "1. 创建 .env 文件并配置 API 密钥"
echo "2. 将 PDF 文件放入 docs/ 目录"
echo "3. 运行 'python main.py ingest' 开始数据摄入"
echo "4. 运行 'python main.py query' 开始问答"
echo "5. 运行 'python examples/chunking_demo.py' 查看分块策略演示"
echo ""
echo "更多信息请查看 README.md" 