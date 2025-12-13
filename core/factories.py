# core/factories.py
from typing import Callable, Dict, Type

# 引入服务组件
from llm_services.abstract_service import AbstractLLMService
from llm_services.openai_service import OpenAIService
from llm_services.gemini_service import GeminiService
from llm_services.ollama_service import OllamaService

from static_analyzers.abstract_analyzer import AbstractStaticAnalyzer
from static_analyzers.slither_analyzer import SlitherAnalyzer
from static_analyzers.soteria_analyzer import SoteriaAnalyzer

from config.settings import llm_settings, project_settings

class ServiceFactory:
    """
    负责实例化 LLM 服务和静态分析器的工厂类。
    使用字典映射替代 if-else，实现解耦。
    """

    # --- LLM 生产线 ---
    @staticmethod
    def create_openai_service() -> AbstractLLMService:
        if not project_settings.OPENAI_API_KEY:
            raise ValueError("配置错误: 使用 OpenAI 服务需要设置 OPENAI_API_KEY")
        return OpenAIService()

    @staticmethod
    def create_gemini_service() -> AbstractLLMService:
        if not project_settings.GEMINI_API_KEY:
            raise ValueError("配置错误: 使用 Gemini 服务需要设置 GEMINI_API_KEY")
        return GeminiService()

    @staticmethod
    def create_ollama_service() -> AbstractLLMService:
        # Ollama 不需要 API Key，但需要确保服务可达
        return OllamaService()

    # LLM 注册表：将模型关键字映射到创建函数
    # 只要模型名称包含 key (如 "gpt-4o" 包含 "gpt")，就使用对应的工厂
    _LLM_REGISTRY: Dict[str, Callable[[], AbstractLLMService]] = {
        "gpt": create_openai_service,
        "openai": create_openai_service,
        "gemini": create_gemini_service,
        "llama": create_ollama_service,
        "qwen": create_ollama_service,
        "mistral": create_ollama_service,
        "deepseek": create_ollama_service,
        "ollama": create_ollama_service,
    }

    @classmethod
    def get_llm_service(cls) -> AbstractLLMService:
        """根据配置的模型名称，自动分发对应的服务实例"""
        model_name = llm_settings.MODEL_NAME.lower()
        
        for keyword, creator_func in cls._LLM_REGISTRY.items():
            if keyword in model_name:
                print(f"🏭 Factory: 根据模型名 '{model_name}' 加载 -> {creator_func.__name__}")
                return creator_func()
        
        raise ValueError(f"🏭 Factory: 未知的模型配置 '{model_name}'。支持: {list(cls._LLM_REGISTRY.keys())}")

    # --- 静态分析器生产线 ---
    
    # 静态分析器注册表：将 ProjectType 映射到类
    _ANALYZER_REGISTRY: Dict[str, Type[AbstractStaticAnalyzer]] = {
        "EVM": SlitherAnalyzer,
        "SOLANA": SoteriaAnalyzer,
    }

    @classmethod
    def get_static_analyzer(cls) -> AbstractStaticAnalyzer:
        """根据项目类型配置，自动分发对应的分析器实例"""
        project_type = project_settings.PROJECT_TYPE
        
        analyzer_class = cls._ANALYZER_REGISTRY.get(project_type)
        
        if not analyzer_class:
            raise NotImplementedError(f"🏭 Factory: 项目类型 '{project_type}' 的分析器尚未实现或注册。")
            
        print(f"🏭 Factory: 根据项目类型 '{project_type}' 加载 -> {analyzer_class.__name__}")
        return analyzer_class()