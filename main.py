import click

from app.cli.ingest import ingest
from app.cli.query import query


@click.group()
def cli():
    """一个用于 RAG 应用的命令行工具。"""
    pass


cli.add_command(ingest)
cli.add_command(query)


if __name__ == "__main__":
    cli() 