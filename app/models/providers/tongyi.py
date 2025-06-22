"""通义千问模型提供者"""

import os
from langchain_community.llms import Tongyi
from langchain_core.language_models import BaseLLM
from ..base import LLMProvider
from app.core.exceptions import ConfigurationError, ServiceError
from app.models.wrappers import create_robust_wrapper


class TongyiProvider(LLMProvider):
    """通义千问模型提供者"""
    
    def __init__(self, model_name: str = "qwen-turbo", temperature: float = 0.1):
        self.model_name = model_name
        self.temperature = temperature
        self._api_key = self._get_api_key()
    
    def _get_api_key(self) -> str:
        """获取通义千问 API 密钥"""
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            raise ConfigurationError(
                "在环境变量中找不到 DASHSCOPE_API_KEY。\n"
                "请在您的 .env 文件中进行设置。\n"
                "示例：DASHSCOPE_API_KEY=your_api_key_here"
            )
        return api_key
    
    def create_llm(self) -> BaseLLM:
        """创建通义千问模型实例"""
        try:
            # 创建基础的Tongyi实例
            base_llm = Tongyi(
                model_name=self.model_name,
                dashscope_api_key=self._api_key,
                temperature=self.temperature,
            )
            
            # 使用通用包装器包装
            return create_robust_wrapper(
                llm_instance=base_llm,
                provider_name="通义千问",
                max_retries=3,
                retry_delay=1,
                custom_error_patterns=self._get_tongyi_error_patterns()
            )
        except Exception as e:
            raise ServiceError(
                f"创建通义千问模型失败：{e}\n"
                f"请检查模型名称 '{self.model_name}' 是否正确，"
                f"以及API密钥是否有效。"
            )
    
    def _get_tongyi_error_patterns(self):
        """获取通义千问特定的错误模式"""
        return {
            "quota_error": {
                "keywords": ["quota", "limit", "account", "rate", "balance", "credit", "欠费", "余额不足", "arrearage"],
                "message": "通义千问API调用失败：账户余额不足或配额超限。\n请检查您的账户余额或联系客服。",
                "retry": False
            },
            "network_error": {
                "keywords": ["timeout", "connection", "network", "网络", "连接"],
                "message": "网络连接失败，已重试 {retry_count} 次。\n请检查网络连接或稍后重试。",
                "retry": True
            },
            "auth_error": {
                "keywords": ["invalid", "auth", "unauthorized", "认证", "授权"],
                "message": "API认证失败：请检查您的API密钥是否正确。",
                "retry": False
            },
            "unknown_error": {
                "keywords": [],
                "message": "通义千问API调用失败：{error}\n请稍后重试或联系技术支持。",
                "retry": True
            }
        }
    
    def get_provider_name(self) -> str:
        return "通义千问"
    
    def test_connection(self) -> bool:
        """测试API连接"""
        try:
            llm = self.create_llm()
            # 发送一个简单的测试请求
            test_response = llm.invoke("你好, 你只需要回答你好")
            return True
        except Exception as e:
            print(f"通义千问API连接测试失败：{e}")
            return False 