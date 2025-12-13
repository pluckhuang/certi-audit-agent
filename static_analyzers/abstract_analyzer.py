# static_analyzers/abstract_analyzer.py
from abc import ABC, abstractmethod

class AbstractStaticAnalyzer(ABC):
    """
    静态分析器抽象基类 (Strategy Interface)
    """
    
    @abstractmethod
    def check_installed(self) -> bool:
        """检查底层工具是否安装"""
        pass

    @abstractmethod
    def run_analysis(self, file_path: str) -> str:
        """
        运行分析并返回对 LLM 友好的摘要字符串。
        """
        pass