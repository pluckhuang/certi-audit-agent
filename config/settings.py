# config/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

# 定义支持的链/语言类型
ProjectType = Literal['EVM', 'SOLANA', 'MOVE']

class LLMSettings(BaseSettings):
    """LLM 模型配置"""
    model_config = SettingsConfigDict(env_prefix='LLM_') 

    MODEL_NAME: str = "gpt-4o"
    TEMPERATURE: float = 0.1
    TIMEOUT: int = 60 
    SEVERITY_LEVELS: Literal['High', 'Medium', 'Low', 'Informational'] = 'High'

class ProjectSettings(BaseSettings):
    """项目环境配置"""
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    
    # 项目类型，默认为 EVM
    PROJECT_TYPE: ProjectType = 'EVM'
    
    OPENAI_API_KEY: str = "" 
    GEMINI_API_KEY: str = "" 
    OLLAMA_BASE_URL: str = "http://localhost:11434/v1" # 默认 Ollama 地址
    SECURITY_BEST_PRACTICES_PATH: str = "config/best_practices.txt"

llm_settings = LLMSettings()
project_settings = ProjectSettings()