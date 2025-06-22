import click
import questionary
from app.services import qa_service, vector_store_service
from app.core.exceptions import ServiceError

@click.command(name="query", help="使用用户提供的问题查询向量库。")
def query():
    """
    使用用户提供的问题查询向量库。
    """
    try:
        click.secho("正在加载嵌入模型...", fg="blue")
        embeddings = qa_service.load_embedding_model()

        click.secho("正在加载向量库...", fg="blue")
        vector_store = vector_store_service.load_vector_store(embeddings)

        if not vector_store:
            click.secho(
                "未找到向量库。请先运行 'python main.py ingest'。",
                fg="red",
            )
            return

        click.secho("正在加载大语言模型...", fg="blue")
        try:
            llm = qa_service.load_llm()
        except Exception as e:
            click.secho("加载大语言模型失败... 错误信息:"+str(e), fg="red")
            return

        click.secho("正在创建问答链...", fg="blue")
        try:
            qa_chain = qa_service.create_qa_chain(vector_store, llm)
        except Exception as e:
            click.secho("创建问答链失败... 错误信息:"+str(e), fg="red")
            return

        click.secho("✅ 已准备好回答您的问题！", fg="green")
        click.secho("💡 提示：输入 'exit' 退出，输入 'help' 查看帮助", fg="cyan")

        while True:
            try:
                query_text = questionary.text(
                    "请输入您的问题:"
                ).ask()

                if not query_text or query_text is None or query_text.lower() == "exit":
                    click.echo("正在退出。")
                    break
                    
                if query_text.lower() == "help":
                    click.secho("\n📖 使用帮助：", fg="blue", bold=True)
                    click.echo("• 直接输入问题即可获得答案")
                    click.echo("• 输入 'exit' 退出程序")
                    click.echo("• 输入 'help' 查看此帮助")
                    click.echo("• 如果遇到错误，系统会自动重试")
                    click.echo("• 支持连续对话，上下文会自动保持")
                    click.echo()
                    continue

                click.secho("\n🤔 正在思考...", fg="cyan")

                try:
                    result = qa_service.ask_question(qa_chain, query_text)
                    
                    # 检查结果
                    if not result or not result.get("result"):
                        click.secho("⚠️ 模型返回了空结果，请重试", fg="yellow")
                        continue
                    
                    # 显示答案
                    click.secho("\n💡 答案:", fg="green", bold=True)
                    click.echo(result["result"])

                    # 显示来源文档
                    if result.get("source_documents"):
                        click.secho("\n📚 来源文档:", fg="yellow", bold=True)
                        for i, doc in enumerate(result["source_documents"], 1):
                            source_info = {
                                "source": doc.metadata.get("source", "N/A"),
                                "page": doc.metadata.get("page", "N/A"),
                            }
                            click.echo(f"{i}. 来源: {source_info['source']}, 页码: {source_info['page']}")
                    else:
                        click.secho("\n⚠️ 未找到相关来源文档", fg="yellow")
                        
                    click.echo("-" * 50)
                except ServiceError as e:
                    click.secho("调用模型错误:"+str(e), fg="yellow")
                    continue
                except Exception as e:
                    click.secho("调用出现错误:"+str(e), fg="yellow")
                    continue
                    
            except KeyboardInterrupt:
                click.echo("正在退出...")
                break
            finally:
                break
                
    except KeyboardInterrupt:
        click.echo("\n\n程序被用户中断")
        return
    except Exception as e:
        click.secho("运行出现错误"+str(e), fg="red")
        click.secho("\n🔧 故障排除建议：", fg="yellow", bold=True)
        click.echo("1. 检查 .env 文件配置")
        click.echo("2. 确认所有依赖已安装")
        click.echo("3. 运行 'python main.py ingest' 重新摄入数据")
        click.echo("4. 查看详细错误日志") 