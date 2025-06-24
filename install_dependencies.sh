#!/bin/bash

# RAG 项目一键安装脚本

echo "🚀 RAG 项目一键安装脚本"
echo "========================"

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

# 安装缺失的依赖包
echo "📦 安装缺失的依赖包..."
pip install rank_bm25 FlagEmbedding huggingface_hub

# 检查 Ollama 安装
echo "🔍 检查 Ollama 安装..."
if ! command -v ollama &> /dev/null; then
    echo "⚠️ 未检测到 Ollama，是否安装？(y/n)"
    read -r install_ollama
    if [[ $install_ollama =~ ^[Yy]$ ]]; then
        echo "📥 安装 Ollama..."
        curl -fsSL https://ollama.ai/install.sh | sh
        echo "✅ Ollama 安装完成"
        echo "💡 请运行 'ollama serve' 启动服务"
    else
        echo "⚠️ 跳过 Ollama 安装，如需使用本地模型请手动安装"
    fi
else
    echo "✅ Ollama 已安装"
    # 检查 Ollama 服务状态
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✅ Ollama 服务正在运行"
        
        # 检查模型
        echo "📦 检查 Ollama 模型..."
        models=$(curl -s http://localhost:11434/api/tags | jq -r '.models[].name' 2>/dev/null || echo "")
        if [[ -n "$models" ]]; then
            echo "✅ 已安装的模型:"
            echo "$models" | while read -r model; do
                echo "  - $model"
            done
        else
            echo "⚠️ 未安装任何模型，是否下载常用模型？(y/n)"
            read -r download_models
            if [[ $download_models =~ ^[Yy]$ ]]; then
                echo "📥 下载常用模型..."
                ollama pull nomic-embed-text:latest
                ollama pull qwen2.5:7b
                echo "✅ 模型下载完成"
            fi
        fi
    else
        echo "⚠️ Ollama 服务未运行，请运行 'ollama serve' 启动服务"
    fi
fi

# 下载重排序模型
echo "🤖 下载重排序模型..."
echo "是否下载 BGE reranker 模型？(y/n)"
read -r download_reranker
if [[ $download_reranker =~ ^[Yy]$ ]]; then
    echo "📥 下载 BGE reranker 模型..."
    # 设置 HuggingFace 镜像（可选）
    echo "是否使用 HuggingFace 镜像加速下载？(y/n)"
    read -r use_mirror
    if [[ $use_mirror =~ ^[Yy]$ ]]; then
        export HF_ENDPOINT=https://hf-mirror.com
        echo "🔗 使用 HuggingFace 镜像: $HF_ENDPOINT"
    fi
    
    # 下载模型
    python -c "
import os
from huggingface_hub import snapshot_download
try:
    print('正在下载 BAAI/bge-reranker-v2-m3 模型...')
    model_path = snapshot_download(
        repo_id='BAAI/bge-reranker-v2-m3',
        cache_dir=os.path.expanduser('~/.cache/huggingface/hub')
    )
    print(f'✅ 模型下载完成: {model_path}')
except Exception as e:
    print(f'❌ 模型下载失败: {e}')
    print('💡 可以稍后手动下载或使用在线模型')
"
fi

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

# 创建 .env 文件模板
if [ ! -f ".env" ]; then
    echo "📝 创建 .env 文件模板..."
    cat > .env << EOF
# 通义千问 API 密钥
DASHSCOPE_API_KEY=your_dashscope_api_key_here

# 豆包 API 密钥（可选）
DOUBAO_API_KEY=your_doubao_api_key_here

# Ollama 服务地址（可选，默认 http://localhost:11434）
OLLAMA_BASE_URL=http://localhost:11434
EOF
    echo "✅ .env 文件已创建，请编辑并填入您的 API 密钥"
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
    print(f'❌ 分块策略模块导入失败: {e}')

try:
    from app.services.retrievers.dense import DenseRetriever
    from app.services.retrievers.sparse import SparseRetriever
    from app.services.retrievers.hybrid import HybridRetriever
    print('✅ 成功导入检索器模块')
except Exception as e:
    print(f'❌ 检索器模块导入失败: {e}')

try:
    from app.services.rerankers.local_bge_reranker import LocalBGEReranker
    print('✅ 成功导入重排序模块')
except Exception as e:
    print(f'❌ 重排序模块导入失败: {e}')

try:
    from app.models import LLMFactory
    providers = LLMFactory.get_available_providers()
    print(f'✅ 成功导入模型工厂，可用提供者: {providers}')
except Exception as e:
    print(f'❌ 模型工厂导入失败: {e}')
"

echo ""
echo "🎉 安装完成！"
echo ""
echo "📋 下一步操作："
echo "1. 编辑 .env 文件并配置 API 密钥"
echo "2. 将 PDF 文件放入 docs/ 目录"
echo "3. 运行 'python main.py ingest' 开始数据摄入"
echo "4. 运行 'python main.py query' 开始问答"
echo ""
echo "🔧 可选配置："
echo "- 如需使用 Ollama 本地模型，请确保 Ollama 服务正在运行"
echo "- 如需使用重排序功能，请确保已下载 BGE reranker 模型"
echo "- 如需使用语义分块，请确保已安装 spaCy 模型"
echo ""
echo "更多信息请查看 README.md" 