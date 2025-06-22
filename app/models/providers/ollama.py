"""Ollama 本地模型提供者"""

from langchain_community.llms import Ollama
from langchain_core.language_models import BaseLLM
from ..base import LLMProvider
from app.core.config import OLLAMA_BASE_URL


class OllamaProvider(LLMProvider):
    """Ollama 本地模型提供者"""
    
    def __init__(self, model_name: str = "qwen2.5:7b", temperature: float = 0.1):
        self.model_name = model_name
        self.temperature = temperature
        self.base_url = OLLAMA_BASE_URL
    
    def create_llm(self) -> BaseLLM:
        """创建 Ollama 模型实例"""
        return Ollama(
            model=self.model_name,
            base_url=self.base_url,
            temperature=self.temperature,
        )
    
    def get_provider_name(self) -> str:
        return "Ollama" 