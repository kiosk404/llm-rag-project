import click
import questionary
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    CharacterTextSplitter,
)

from app.core.config import DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP, DOCS_DIR
from app.services import document_service, vector_store_service, qa_service
import os


@click.command(name="ingest", help="从 'docs' 目录摄入 PDF 文档到向量库。")
def ingest():
    """
    从 'docs' 目录摄入 PDF 文档到向量库。
    """
    if not any(f.endswith('.pdf') for f in os.listdir(DOCS_DIR)):
        click.secho(f"在 {DOCS_DIR} 未找到 PDF 文件。请添加一些 PDF 文件后再试。", fg="red")
        return

    # 获取可用的分块策略
    available_strategies = document_service.get_available_chunking_strategies()
    
    # 显示策略描述
    strategy_choices = []
    for name, description in available_strategies.items():
        strategy_choices.append(f"{name} - {description}")
    
    # 使用 questionary 进行交互式提问
    selected_strategy = questionary.select(
        "请选择文本分割策略:",
        choices=strategy_choices
    ).ask()

    if not selected_strategy:
        click.echo("未选择分割器，操作中止。")
        return
    
    # 提取策略名称
    strategy_name = selected_strategy.split(" - ")[0]

    chunk_size = questionary.text(
        "请输入文本块大小:",
        default=str(DEFAULT_CHUNK_SIZE),
        validate=lambda text: text.isdigit() and int(text) > 0 or "请输入一个有效的正整数"
    ).ask()

    if not chunk_size:
        click.echo("未输入文本块大小，操作中止。")
        return

    chunk_overlap = questionary.text(
        "请输入文本块重叠大小:",
        default=str(DEFAULT_CHUNK_OVERLAP),
        validate=lambda text: text.isdigit() or "请输入一个有效的数字"
    ).ask()

    if not chunk_overlap:
        click.echo("未输入文本块重叠大小，操作中止。")
        return

    chunk_size = int(chunk_size)
    chunk_overlap = int(chunk_overlap)

    click.secho("正在加载文档...", fg="blue")
    docs = document_service.load_documents()

    click.secho(f"正在使用 {strategy_name} 分割文档...", fg="blue")
    chunks = document_service.split_documents_with_strategy_name(
        docs,
        strategy_name=strategy_name,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    click.secho(f"已创建 {len(chunks)} 个文本块。", fg="green")

    click.secho("正在加载嵌入模型...", fg="blue")
    embeddings = qa_service.load_embedding_model()

    click.secho("正在创建并保存向量库...", fg="blue")
    vector_store_service.create_and_save_vector_store(chunks, embeddings)

    click.secho("数据摄入完成！", fg="green") 