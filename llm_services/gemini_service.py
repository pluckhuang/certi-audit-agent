# llm_services/gemini_service.py
import json
from google import genai
from google.genai import types
from typing import Dict, Any

from llm_services.abstract_service import AbstractLLMService
from config.settings import llm_settings, project_settings 

class GeminiService(AbstractLLMService):
    
    def __init__(self):
        # 初始化客户端
        self.client = genai.Client(api_key=project_settings.GEMINI_API_KEY)
        self.model_name = llm_settings.MODEL_NAME  
        self.temperature = llm_settings.TEMPERATURE

    def generate_response(self, system_prompt: str, user_prompt: str, **kwargs) -> Dict[str, Any]:
        
        # 1. 动态构建 Config，将 system_instruction 放入其中
        # 這是解决 'unexpected keyword argument' 错误的关键
        config = types.GenerateContentConfig(
            temperature=self.temperature,
            response_mime_type="application/json", # 强制 JSON
            system_instruction=system_prompt       # <--- 移动到这里！
        )
        
        # 2. 简化的 contents 构造
        # 直接传入字符串列表，SDK 会自动处理，避免 Part.from_text 的错误
        contents = [user_prompt]
        
        try:
            # 3. 调用 API
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config 
            )
            
            # 解析响应
            llm_output_str = response.text.strip()
            
            # 处理可能的 Markdown 代码块包裹 (```json ... ```)
            # 有些模型虽然指定了 JSON 模式，仍可能加上 Markdown 标记
            if llm_output_str.startswith("```json"):
                llm_output_str = llm_output_str.strip("```json").strip("```").strip()
            elif llm_output_str.startswith("```"):
                llm_output_str = llm_output_str.strip("```").strip()

            return json.loads(llm_output_str)

        except Exception as e:
            # 增加打印原始响应以便调试
            print(f"DEBUG: Gemini API 调用出错。")
            raise RuntimeError(f"Gemini API 调用失败或解析错误: {e}")