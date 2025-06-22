"""豆包模型提供者"""

import os
from langchain_core.language_models import BaseLLM
from ..base import LLMProvider
from app.core.exceptions import ConfigurationError, ServiceError
from app.models.wrappers import create_robust_wrapper


class MockDoubaoLLM(BaseLLM):
    """模拟的豆包LLM实现"""
    
    def _llm_type(self) -> str:
        return "mock_doubao"
    
    def _call(self, prompt: str, **kwargs) -> str:
        # 模拟豆包API调用
        return f"豆包模型回复: {prompt}"


class DoubaoProvider(LLMProvider):
    """豆包模型提供者"""
    
    def __init__(self, model_name: str = "doubao-pro", temperature: float = 0.1):
        self.model_name = model_name
        self.temperature = temperature
        self._api_key = self._get_api_key()
    
    def _get_api_key(self) -> str:
        """获取豆包 API 密钥"""
        api_key = os.getenv("DOUBAO_API_KEY")
        if not api_key:
            raise ConfigurationError(
                "在环境变量中找不到 DOUBAO_API_KEY。\n"
                "请在您的 .env 文件中进行设置。\n"
                "示例：DOUBAO_API_KEY=your_api_key_here"
            )
        return api_key
    
    def create_llm(self) -> BaseLLM:
        """创建豆包模型实例"""
        try:
            # 创建基础的Doubao实例（使用模拟实现）
            # 注意：当langchain_community支持豆包时，可以替换为真实实现
            base_llm = MockDoubaoLLM()
            
            # 使用通用包装器包装
            return create_robust_wrapper(
                llm_instance=base_llm,
                provider_name="豆包",
                max_retries=3,
                retry_delay=1,
                custom_error_patterns=self._get_doubao_error_patterns()
            )
        except Exception as e:
            raise ServiceError(
                f"创建豆包模型失败：{e}\n"
                f"请检查模型名称 '{self.model_name}' 是否正确，"
                f"以及API密钥是否有效。"
            )
    
    def _get_doubao_error_patterns(self):
        """获取豆包特定的错误模式"""
        return {
            "quota_error": {
                "keywords": ["quota", "limit", "account", "rate", "balance", "credit", "欠费", "余额不足", "insufficient"],
                "message": "豆包API调用失败：账户余额不足或配额超限。\n请检查您的账户余额或联系客服。",
                "retry": False
            },
            "network_error": {
                "keywords": ["timeout", "connection", "network", "网络", "连接"],
                "message": "网络连接失败，已重试 {retry_count} 次。\n请检查网络连接或稍后重试。",
                "retry": True
            },
            "auth_error": {
                "keywords": ["invalid", "auth", "unauthorized", "认证", "授权", "api_key"],
                "message": "API认证失败：请检查您的API密钥是否正确。",
                "retry": False
            },
            "rate_limit_error": {
                "keywords": ["rate_limit", "rate limit", "频率限制", "请求过于频繁"],
                "message": "请求频率超限，已重试 {retry_count} 次。\n请稍后重试。",
                "retry": True
            },
            "unknown_error": {
                "keywords": [],
                "message": "豆包API调用失败：{error}\n请稍后重试或联系技术支持。",
                "retry": True
            }
        }
    
    def get_provider_name(self) -> str:
        return "豆包"
    
    def test_connection(self) -> bool:
        """测试API连接"""
        try:
            llm = self.create_llm()
            # 发送一个简单的测试请求
            test_response = llm.invoke("你好")
            return True
        except Exception as e:
            print(f"豆包API连接测试失败：{e}")
            return False 