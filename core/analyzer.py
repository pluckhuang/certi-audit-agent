# core/analyzer.py
import json
from pydantic import ValidationError

from llm_services.abstract_service import AbstractLLMService
from core.pydantic_schema import AuditReport
# [🔴] 确保正确导入 settings
from config.settings import project_settings, llm_settings
from config import prompt_templates
# [✨] 引入抽象接口
from static_analyzers.abstract_analyzer import AbstractStaticAnalyzer

class AuditAnalyzer:
    
    # [✨] 依赖注入：接收一个通用的 static_analyzer
    def __init__(self, llm_service: AbstractLLMService, static_analyzer: AbstractStaticAnalyzer):
        self.llm_service = llm_service
        self.static_analyzer = static_analyzer 
        self.report_schema = AuditReport
        self.rag_context = self._load_rag_context()

    def _load_rag_context(self) -> str:
        try:
            with open(project_settings.SECURITY_BEST_PRACTICES_PATH, 'r') as f:
                content = f.read()
            return prompt_templates.RAG_CONTEXT_TEMPLATE.format(best_practices_content=content)
        except FileNotFoundError:
            return "没有可用的安全最佳实践上下文。"

    def analyze(self, file_path: str, contract_code: str) -> AuditReport:
        
        # 1. 🚀 调用多态的静态分析器
        # 无论是 Slither 还是未来的 SolanaAnalyzer，调用方式都一样
        print(f"🔍 [System] 正在运行静态分析 (模式: {project_settings.PROJECT_TYPE})...")
        
        static_result = self.static_analyzer.run_analysis(file_path)
        
        print(f"✅ [System] 静态分析完成。")
        print(f"   (摘要: {static_result[:50].replace(chr(10), ' ')}...)")
        
        schema_json = json.dumps(self.report_schema.model_json_schema(), indent=2)
        
        # 2. 📝 构建混合 Prompt
        system_prompt = prompt_templates.SYSTEM_PROMPT_TEMPLATE
        
        # 使用新的占位符 static_analysis_result
        user_prompt = prompt_templates.USER_PROMPT_TEMPLATE.format(
            rag_context=self.rag_context,
            static_analysis_result=static_result,  
            schema_json=schema_json,
            contract_code=contract_code
        )
        
        # 3. 🧠 调用 LLM
        print(f"🧠 [AI] 正在调用 {llm_settings.MODEL_NAME} 进行语义分析...")
        raw_data = self.llm_service.generate_response(system_prompt, user_prompt)

        # 4. ✅ 验证与返回
        try:
            report = self.report_schema(**raw_data)
            return report
        except ValidationError as e:
            print(f"❌ Pydantic 验证失败")
            raise e