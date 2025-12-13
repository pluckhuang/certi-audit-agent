# llm_services/abstract_service.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class AbstractLLMService(ABC):
    """LLM 服务抽象基类，定义了所有服务必须实现的方法"""
    
    @abstractmethod
    def generate_response(self, system_prompt: str, user_prompt: str, **kwargs) -> Dict[str, Any]:
        """
        根据输入 Prompt 生成响应。
        返回结果必须是经过解析的 Python 字典。
        """
        pass