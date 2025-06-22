#!/usr/bin/env python3
"""
分块策略演示脚本

展示各种文本分块策略的效果和差异。
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.chunking_strategies import ChunkingStrategyFactory
from app.services.document_service import load_documents


def demo_chunking_strategies():
    """演示各种分块策略"""
    
    print("=" * 60)
    print("文本分块策略演示")
    print("=" * 60)
    
    # 检查是否有文档
    docs_dir = Path("docs")
    if not docs_dir.exists() or not any(docs_dir.glob("*.pdf")):
        print("❌ 在 docs 目录中未找到 PDF 文件")
        print("请先添加一些 PDF 文件到 docs 目录")
        return
    
    # 加载文档
    print("📄 正在加载文档...")
    try:
        documents = load_documents()
        print(f"✅ 成功加载 {len(documents)} 个文档")
    except Exception as e:
        print(f"❌ 加载文档失败: {e}")
        return
    
    # 获取所有可用的分块策略
    strategies = ChunkingStrategyFactory.get_available_strategies()
    
    print(f"\n🔧 可用的分块策略 ({len(strategies)} 种):")
    for i, (name, description) in enumerate(strategies.items(), 1):
        print(f"  {i}. {name}")
        print(f"     {description}")
        print()
    
    # 演示每种策略
    print("=" * 60)
    print("分块策略效果演示")
    print("=" * 60)
    
    # 使用第一个文档进行演示
    if documents:
        demo_doc = documents[0]
        print(f"📝 演示文档: {demo_doc.metadata.get('source', '未知')}")
        print(f"📏 文档长度: {len(demo_doc.page_content)} 字符")
        print()
        
        # 截取前500字符作为演示
        demo_text = demo_doc.page_content[:500] + "..." if len(demo_doc.page_content) > 500 else demo_doc.page_content
        print(f"📄 文档内容预览:\n{demo_text}\n")
        
        # 为演示创建临时文档
        temp_doc = type('Document', (), {
            'page_content': demo_doc.page_content,
            'metadata': demo_doc.metadata
        })()
        
        for strategy_name in strategies.keys():
            try:
                print(f"🔧 测试策略: {strategy_name}")
                strategy = ChunkingStrategyFactory.get_strategy(strategy_name)
                
                # 使用较小的chunk_size进行演示
                chunks = strategy.split_documents(
                    [temp_doc], 
                    chunk_size=200, 
                    chunk_overlap=20
                )
                
                print(f"   ✅ 成功创建 {len(chunks)} 个文本块")
                
                # 显示前3个块的内容预览
                for i, chunk in enumerate(chunks[:3], 1):
                    preview = chunk.page_content[:100] + "..." if len(chunk.page_content) > 100 else chunk.page_content
                    print(f"   块 {i}: {preview}")
                
                if len(chunks) > 3:
                    print(f"   ... 还有 {len(chunks) - 3} 个块")
                print()
                
            except Exception as e:
                print(f"   ❌ 策略执行失败: {e}")
                print()
    
    print("=" * 60)
    print("演示完成！")
    print("=" * 60)
    print("\n💡 使用提示:")
    print("1. 固定大小分块: 适合需要严格控制块大小的场景")
    print("2. 重叠分块: 适合需要保持上下文连贯性的场景")
    print("3. 递归分块: 适合大多数文档，智能识别自然边界")
    print("4. Token分块: 适合与LLM配合使用")
    print("5. Markdown分块: 适合Markdown格式文档")
    print("6. 语义分块: 适合需要保持语义完整性的场景")
    print("\n🚀 运行 'python main.py ingest' 开始使用这些策略！")


if __name__ == "__main__":
    demo_chunking_strategies() 