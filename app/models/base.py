"""模型基类定义"""

from abc import ABC, abstractmethod
from langchain_core.language_models import BaseLLM


class LLMProvider(ABC):
    """大语言模型提供者抽象基类"""
    
    @abstractmethod
    def create_llm(self) -> BaseLLM:
        """创建大语言模型实例"""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """获取提供者名称"""
        pass 