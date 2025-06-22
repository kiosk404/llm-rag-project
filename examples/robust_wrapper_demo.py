#!/usr/bin/env python3
"""
通用模型包装器演示脚本
展示如何使用 RobustLLMWrapper 包装不同的模型提供者
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.wrappers import RobustLLMWrapper, create_robust_wrapper
from app.models.factory import LLMFactory
from langchain_core.language_models import BaseLLM


def demo_basic_wrapper():
    """演示基础包装器使用"""
    print("=" * 50)
    print("演示1：基础包装器使用")
    print("=" * 50)
    
    # 创建一个模拟的LLM实例（这里用字符串模拟）
    class MockLLM(BaseLLM):
        def _llm_type(self) -> str:
            return "mock"
        
        def _call(self, prompt: str, **kwargs) -> str:
            # 模拟网络错误
            if "error" in prompt.lower():
                raise Exception("模拟网络连接错误")
            return f"MockLLM回复: {prompt}"
        def _generate(self, prompts, stop=None, run_manager=None, **kwargs):
            # 简单实现，返回每个prompt的_mock回复
            return type('LLMResult', (), {"generations": [[{"text": self._call(p)}] for p in prompts]})()
    
    # 使用包装器包装
    mock_llm = MockLLM()
    robust_llm = create_robust_wrapper(
        llm_instance=mock_llm,
        provider_name="Mock模型",
        max_retries=2,
        retry_delay=1
    )
    
    print("✅ 包装器创建成功")
    print(f"模型类型: {robust_llm._llm_type()}")
    
    # 测试正常调用
    try:
        result = robust_llm.invoke("你好")
        print(f"正常调用结果: {result}")
    except Exception as e:
        print(f"调用失败: {e}")
    
    print()


def demo_custom_error_patterns():
    """演示自定义错误模式"""
    print("=" * 50)
    print("演示2：自定义错误模式")
    print("=" * 50)
    
    class MockLLM(BaseLLM):
        def _llm_type(self) -> str:
            return "mock"
        
        def _call(self, prompt: str, **kwargs) -> str:
            if "quota" in prompt.lower():
                raise Exception("账户余额不足，请充值")
            elif "auth" in prompt.lower():
                raise Exception("API密钥无效")
            elif "network" in prompt.lower():
                raise Exception("网络连接超时")
            return f"MockLLM回复: {prompt}"
        def _generate(self, prompts, stop=None, run_manager=None, **kwargs):
            return type('LLMResult', (), {"generations": [[{"text": self._call(p)}] for p in prompts]})()
    
    # 自定义错误模式
    custom_patterns = {
        "quota_error": {
            "keywords": ["余额不足", "quota", "balance"],
            "message": "自定义错误：账户余额不足，请及时充值。",
            "retry": False
        },
        "auth_error": {
            "keywords": ["密钥无效", "auth", "unauthorized"],
            "message": "自定义错误：API密钥验证失败。",
            "retry": False
        },
        "network_error": {
            "keywords": ["网络", "timeout", "connection"],
            "message": "自定义错误：网络连接问题，正在重试...",
            "retry": True
        }
    }
    
    mock_llm = MockLLM()
    robust_llm = create_robust_wrapper(
        llm_instance=mock_llm,
        provider_name="自定义模型",
        max_retries=2,
        retry_delay=1,
        custom_error_patterns=custom_patterns
    )
    
    # 测试不同类型的错误
    test_cases = [
        "正常问题",
        "quota测试",
        "auth测试", 
        "network测试"
    ]
    
    for test_case in test_cases:
        try:
            result = robust_llm.invoke(test_case)
            print(f"✅ {test_case}: {result}")
        except Exception as e:
            print(f"❌ {test_case}: {e}")
    
    print()


def demo_real_providers():
    """演示真实模型提供者"""
    print("=" * 50)
    print("演示3：真实模型提供者")
    print("=" * 50)
    
    available_providers = LLMFactory.get_available_providers()
    print(f"可用的模型提供者: {available_providers}")
    
    # 测试通义千问提供者（如果配置了API密钥）
    if "tongyi" in available_providers:
        try:
            provider = LLMFactory.create_provider("tongyi")
            llm = provider.create_llm()
            print(f"✅ 通义千问模型创建成功: {llm._llm_type()}")
            
            # 测试连接（如果API密钥有效）
            if provider.test_connection():
                print("✅ 通义千问API连接测试成功")
            else:
                print("⚠️ 通义千问API连接测试失败（可能是API密钥问题）")
                
        except Exception as e:
            print(f"❌ 通义千问模型创建失败: {e}")
    
    # 测试豆包提供者（如果配置了API密钥）
    if "doubao" in available_providers:
        try:
            provider = LLMFactory.create_provider("doubao")
            llm = provider.create_llm()
            print(f"✅ 豆包模型创建成功: {llm._llm_type()}")
            
            # 测试连接（如果API密钥有效）
            if provider.test_connection():
                print("✅ 豆包API连接测试成功")
            else:
                print("⚠️ 豆包API连接测试失败（可能是API密钥问题）")
                
        except Exception as e:
            print(f"❌ 豆包模型创建失败: {e}")
    
    print()


def demo_wrapper_features():
    """演示包装器特性"""
    print("=" * 50)
    print("演示4：包装器特性")
    print("=" * 50)
    
    class MockLLM(BaseLLM):
        def _llm_type(self) -> str:
            return "mock"
        
        def _call(self, prompt: str, **kwargs) -> str:
            return f"MockLLM回复: {prompt}"
        def _generate(self, prompts, stop=None, run_manager=None, **kwargs):
            return type('LLMResult', (), {"generations": [[{"text": self._call(p)}] for p in prompts]})()
    
    mock_llm = MockLLM()
    robust_llm = create_robust_wrapper(
        llm_instance=mock_llm,
        provider_name="特性演示模型",
        max_retries=3,
        retry_delay=1
    )
    
    print("包装器特性:")
    print(f"• 最大重试次数: {robust_llm._max_retries}")
    print(f"• 重试延迟: {robust_llm._retry_delay}秒")
    print(f"• 提供者名称: {robust_llm._provider_name}")
    print(f"• 模型类型: {robust_llm._llm_type()}")
    
    # 演示动态添加错误模式
    robust_llm.add_error_pattern(
        error_type="custom_error",
        keywords=["自定义", "custom"],
        message="这是一个自定义错误模式",
        retry=True
    )
    
    print("• 支持动态添加错误模式")
    print()


if __name__ == "__main__":
    print("🚀 通用模型包装器演示")
    print()
    
    demo_basic_wrapper()
    demo_custom_error_patterns()
    demo_real_providers()
    demo_wrapper_features()
    
    print("=" * 50)
    print("演示完成！")
    print("=" * 50)
    print()
    print("💡 使用提示:")
    print("1. 通用包装器可以包装任何继承自BaseLLM的模型")
    print("2. 支持自定义错误模式和重试策略")
    print("3. 可以轻松扩展支持新的模型提供者")
    print("4. 提供了统一的错误处理和重试机制") 