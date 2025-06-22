"""模型工厂类"""

from typing import Dict, Type
from .base import LLMProvider
from .providers.tongyi import TongyiProvider
from .providers.doubao import DoubaoProvider
from .providers.ollama import OllamaProvider
from app.core.exceptions import LLMProviderError


class LLMFactory:
    """大语言模型工厂类"""
    
    _providers: Dict[str, Type[LLMProvider]] = {
        "tongyi": TongyiProvider,
        "doubao": DoubaoProvider,
        "ollama": OllamaProvider,
    }
    
    @classmethod
    def register_provider(cls, name: str, provider_class: Type[LLMProvider]):
        """注册新的模型提供者"""
        cls._providers[name] = provider_class
    
    @classmethod
    def create_provider(cls, provider_name: str, **kwargs) -> LLMProvider:
        """创建模型提供者实例"""
        if provider_name not in cls._providers:
            raise LLMProviderError(f"不支持的模型提供者: {provider_name}")
        
        provider_class = cls._providers[provider_name]
        return provider_class(**kwargs)
    
    @classmethod
    def get_available_providers(cls) -> list:
        """获取所有可用的模型提供者"""
        return list(cls._providers.keys()) 