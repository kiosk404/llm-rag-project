"""通用模型包装器，提供错误处理和重试机制"""

import time
from typing import Optional, Dict, Any, Callable
from langchain_core.language_models import BaseLLM
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.outputs import LLMResult
from app.core.exceptions import ServiceError
from pydantic import PrivateAttr


class RobustLLMWrapper(BaseLLM):
    """通用的LLM包装器，具有错误处理和重试机制"""
    
    _max_retries: int = PrivateAttr(default=3)
    _retry_delay: int = PrivateAttr(default=1)
    _provider_name: str = PrivateAttr(default="未知模型")
    _error_patterns: Dict[str, Dict[str, Any]] = PrivateAttr(default_factory=dict)
    
    def __init__(self, 
                 llm_instance: BaseLLM,
                 provider_name: str = "未知模型",
                 max_retries: int = 3,
                 retry_delay: int = 1,
                 error_patterns: Optional[Dict[str, Dict[str, Any]]] = None):
        """
        初始化包装器
        
        Args:
            llm_instance: 要包装的LLM实例
            provider_name: 模型提供者名称
            max_retries: 最大重试次数
            retry_delay: 重试延迟（秒）
            error_patterns: 错误模式配置
        """
        super().__init__()
        self._llm = llm_instance
        self._provider_name = provider_name
        self._max_retries = max_retries
        self._retry_delay = retry_delay
        
        # 设置默认错误模式
        self._error_patterns = error_patterns or self._get_default_error_patterns()
    
    def _get_default_error_patterns(self) -> Dict[str, Dict[str, Any]]:
        """获取默认的错误模式配置"""
        return {
            "quota_error": {
                "keywords": ["quota", "limit", "account", "rate", "balance", "credit", "欠费", "余额不足"],
                "message": f"{self._provider_name}API调用失败：账户余额不足或配额超限。\n请检查您的账户余额或联系客服。",
                "retry": False
            },
            "network_error": {
                "keywords": ["timeout", "connection", "network", "网络", "连接"],
                "message": f"网络连接失败，已重试 {{retry_count}} 次。\n请检查网络连接或稍后重试。",
                "retry": True
            },
            "auth_error": {
                "keywords": ["invalid", "auth", "unauthorized", "认证", "授权"],
                "message": f"API认证失败：请检查您的API密钥是否正确。",
                "retry": False
            },
            "unknown_error": {
                "keywords": [],
                "message": f"{self._provider_name}API调用失败：{{error}}\n请稍后重试或联系技术支持。",
                "retry": True
            }
        }
    
    def _llm_type(self) -> str:
        """返回模型类型标识"""
        return f"robust_{self._provider_name.lower()}"
    
    def _generate(
        self,
        prompts: list[str],
        stop: Optional[list] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs,
    ) -> LLMResult:
        """实现抽象方法 _generate"""
        if len(prompts) == 1:
            result = self._call(prompts[0], stop, run_manager, **kwargs)
            return LLMResult(generations=[[{"text": result}]])
        else:
            generations = []
            for prompt in prompts:
                result = self._call(prompt, stop, run_manager, **kwargs)
                generations.append([{"text": result}])
            return LLMResult(generations=generations)
    
    def _call(
        self,
        prompt: str,
        stop: Optional[list] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs,
    ) -> str:
        """重写调用方法，添加重试机制和错误处理"""
        last_error = None
        
        for attempt in range(self._max_retries):
            try:
                # 尝试调用底层的LLM实例
                if hasattr(self._llm, 'invoke'):
                    return self._llm.invoke(prompt, stop=stop, **kwargs)
                elif hasattr(self._llm, '_call'):
                    return self._llm._call(prompt, stop=stop, **kwargs)
                else:
                    raise ServiceError(f"不支持的LLM实例类型：{type(self._llm)}")
                    
            except Exception as e:
                last_error = e
                error_msg = str(e).lower()
                
                # 分析错误类型
                error_type = self._analyze_error(error_msg)
                error_config = self._error_patterns.get(error_type, self._error_patterns["unknown_error"])
                
                # 如果不需要重试，直接抛出错误
                if not error_config.get("retry", True):
                    message = error_config["message"].format(
                        error=str(e),
                        retry_count=self._max_retries
                    )
                    raise ServiceError(f"错误详情：{e}\n{message}")
                
                # 如果需要重试且还有重试机会
                if attempt < self._max_retries - 1:
                    retry_message = f"{error_type.replace('_', ' ').title()}错误，正在重试 ({attempt + 1}/{self._max_retries})..."
                    print(retry_message)
                    time.sleep(self._retry_delay * (attempt + 1))
                    continue
                else:
                    # 最后一次重试失败
                    message = error_config["message"].format(
                        error=str(e),
                        retry_count=self._max_retries
                    )
                    raise ServiceError(f"错误详情：{e}\n{message}")
        
        # 如果所有重试都失败了
        raise ServiceError(f"{self._provider_name}API调用失败，已重试 {self._max_retries} 次：{last_error}")
    
    def _analyze_error(self, error_msg: str) -> str:
        """分析错误类型"""
        for error_type, config in self._error_patterns.items():
            if error_type == "unknown_error":
                continue
            keywords = config.get("keywords", [])
            if any(keyword in error_msg for keyword in keywords):
                return error_type
        return "unknown_error"
    
    def add_error_pattern(self, error_type: str, keywords: list, message: str, retry: bool = True):
        """添加自定义错误模式"""
        self._error_patterns[error_type] = {
            "keywords": keywords,
            "message": message,
            "retry": retry
        }


def create_robust_wrapper(llm_instance: BaseLLM, 
                         provider_name: str,
                         max_retries: int = 3,
                         retry_delay: int = 1,
                         custom_error_patterns: Optional[Dict[str, Dict[str, Any]]] = None) -> RobustLLMWrapper:
    """
    创建通用模型包装器的工厂函数
    
    Args:
        llm_instance: 要包装的LLM实例
        provider_name: 模型提供者名称
        max_retries: 最大重试次数
        retry_delay: 重试延迟（秒）
        custom_error_patterns: 自定义错误模式
    
    Returns:
        RobustLLMWrapper: 包装后的LLM实例
    """
    return RobustLLMWrapper(
        llm_instance=llm_instance,
        provider_name=provider_name,
        max_retries=max_retries,
        retry_delay=retry_delay,
        error_patterns=custom_error_patterns
    ) 