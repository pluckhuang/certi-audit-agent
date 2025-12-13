# llm_services/openai_service.py
import json
from openai import OpenAI
from typing import Dict, Any

from llm_services.abstract_service import AbstractLLMService
from config.settings import llm_settings, project_settings 

class OpenAIService(AbstractLLMService):
    
    def __init__(self):
        self.client = OpenAI(api_key=project_settings.OPENAI_API_KEY)
        self.model_name = llm_settings.MODEL_NAME
        self.temperature = llm_settings.TEMPERATURE
        self.timeout = llm_settings.TIMEOUT

    def generate_response(self, system_prompt: str, user_prompt: str, **kwargs) -> Dict[str, Any]:
        
        try:
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
            return json.loads(llm_output_str)

        except Exception as e:
            raise RuntimeError(f"OpenAI API 调用失败或解析错误: {e}")