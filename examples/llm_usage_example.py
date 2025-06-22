#!/usr/bin/env python3
"""
大语言模型使用示例

这个文件展示了如何使用新的工厂模式和策略模式来使用不同的大语言模型。
"""

from app.models import LLMFactory, TongyiProvider, DoubaoProvider, OllamaProvider
from app.services.qa_service import QAService
from app.core.exceptions import LLMProviderError, ConfigurationError


def example_basic_usage():
    """基本使用示例"""
    print("=== 基本使用示例 ===")
    
    # 使用默认配置创建问答服务
    qa_service = QAService()
    print(f"当前使用的模型提供者: {qa_service.llm_provider.get_provider_name()}")
    
    # 加载嵌入模型
    embedding_model = qa_service.load_embedding_model()
    print(f"嵌入模型已加载: {embedding_model.model}")


def example_factory_usage():
    """工厂模式使用示例"""
    print("\n=== 工厂模式使用示例 ===")
    
    # 查看所有可用的模型提供者
    available_providers = LLMFactory.get_available_providers()
    print(f"可用的模型提供者: {available_providers}")
    
    # 创建不同的模型提供者
    try:
        # 创建通义千问提供者
        tongyi_provider = LLMFactory.create_provider("tongyi", model_name="qwen-turbo")
        print(f"创建了 {tongyi_provider.get_provider_name()} 提供者")
        
        # 创建 Ollama 提供者
        ollama_provider = LLMFactory.create_provider("ollama", model_name="qwen2.5:7b")
        print(f"创建了 {ollama_provider.get_provider_name()} 提供者")
        
    except Exception as e:
        print(f"创建提供者时出错: {e}")


def example_custom_provider():
    """自定义提供者示例"""
    print("\n=== 自定义提供者示例 ===")
    
    # 创建自定义的通义千问提供者
    custom_tongyi = TongyiProvider(model_name="qwen-plus", temperature=0.2)
    
    # 使用自定义提供者创建问答服务
    qa_service = QAService(llm_provider=custom_tongyi)
    print(f"使用自定义提供者: {qa_service.llm_provider.get_provider_name()}")
    print(f"模型名称: {custom_tongyi.model_name}")
    print(f"温度参数: {custom_tongyi.temperature}")


def example_provider_registration():
    """注册新提供者示例"""
    print("\n=== 注册新提供者示例 ===")
    
    # 创建一个新的模型提供者类
    class CustomProvider(TongyiProvider):
        def __init__(self, model_name: str = "custom-model", temperature: float = 0.1):
            super().__init__(model_name, temperature)
        
        def get_provider_name(self) -> str:
            return "自定义提供者"
    
    # 注册新的提供者
    LLMFactory.register_provider("custom", CustomProvider)
    
    # 查看更新后的可用提供者
    available_providers = LLMFactory.get_available_providers()
    print(f"注册后的可用提供者: {available_providers}")
    
    # 使用新注册的提供者
    try:
        custom_provider = LLMFactory.create_provider("custom", model_name="my-model")
        print(f"成功创建自定义提供者: {custom_provider.get_provider_name()}")
    except Exception as e:
        print(f"创建自定义提供者时出错: {e}")


def example_error_handling():
    """错误处理示例"""
    print("\n=== 错误处理示例 ===")
    
    # 尝试创建不存在的提供者
    try:
        non_existent_provider = LLMFactory.create_provider("non-existent")
    except LLMProviderError as e:
        print(f"预期的错误: {e}")
    
    # 尝试创建豆包提供者（可能没有配置 API 密钥）
    try:
        doubao_provider = LLMFactory.create_provider("doubao")
        print("豆包提供者创建成功")
    except ConfigurationError as e:
        print(f"豆包提供者创建失败: {e}")


if __name__ == "__main__":
    print("大语言模型使用示例")
    print("=" * 50)
    
    example_basic_usage()
    example_factory_usage()
    example_custom_provider()
    example_provider_registration()
    example_error_handling()
    
    print("\n示例执行完成！") 