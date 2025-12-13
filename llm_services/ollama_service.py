# llm_services/ollama_service.py
import json
from openai import OpenAI
from typing import Dict, Any

from llm_services.abstract_service import AbstractLLMService
from config.settings import llm_settings, project_settings 

class OllamaService(AbstractLLMService):
    """
    使用 Ollama 运行本地大模型。
    Ollama 提供了兼容 OpenAI 的 API 接口。
    """
    
    def __init__(self):
        # 初始化客户端，指向本地 Ollama 服务
        self.client = OpenAI(
            base_url=project_settings.OLLAMA_BASE_URL,
            api_key="ollama" # Ollama 不需要真实的 API Key，但库要求非空
        )
        self.model_name = llm_settings.MODEL_NAME
        self.temperature = llm_settings.TEMPERATURE
        self.timeout = llm_settings.TIMEOUT * 2 # 本地推理可能较慢，增加超时时间

    def generate_response(self, system_prompt: str, user_prompt: str, **kwargs) -> Dict[str, Any]:
        
        try:
            print(f"🦙 [Ollama] 正在调用本地模型: {self.model_name}...")
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                timeout=self.timeout,
                response_format={"type": "json_object"} 
            )
            
            llm_output_str = response.choices[0].message.content.strip()
            
            # 简单的 Markdown 清理 (有些本地模型喜欢加 ```json)
            if llm_output_str.startswith("```json"):
                llm_output_str = llm_output_str[7:]
            elif llm_output_str.startswith("```"):
                llm_output_str = llm_output_str[3:]
            
            if llm_output_str.endswith("```"):
                llm_output_str = llm_output_str[:-3]
                
            return json.loads(llm_output_str.strip())

        except Exception as e:
            raise RuntimeError(f"Ollama 本地调用失败: {e}. 请确保 Ollama 已启动且模型 '{self.model_name}' 已下载 (ollama pull {self.model_name})")
