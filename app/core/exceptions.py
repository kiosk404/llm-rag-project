"""自定义异常类"""


class LLMProviderError(Exception):
    """大语言模型提供者相关异常"""
    pass


class ConfigurationError(Exception):
    """配置相关异常"""
    pass


class ServiceError(Exception):
    """服务相关异常"""
    pass 