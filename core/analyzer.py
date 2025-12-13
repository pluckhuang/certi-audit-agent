# core/analyzer.py
import json
import subprocess
from typing import Optional
from pydantic import ValidationError

from llm_services.abstract_service import AbstractLLMService
from core.pydantic_schema import AuditReport
from config.settings import project_settings, llm_settings
from config import prompt_templates
from static_analyzers.abstract_analyzer import AbstractStaticAnalyzer

class AuditAnalyzer:
    
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

    def _flatten_contract(self, file_path: str) -> Optional[str]:
        """
        尝试简单的递归扁平化合约代码 (解决 Dependency Hell)。
        不支持复杂的重映射 (remappings)，仅支持相对路径导入。
        """
        import re
        import os

        def resolve_imports(current_file_path, visited=None):
            if visited is None:
                visited = set()
            
            if current_file_path in visited:
                return "" # 避免循环导入
            visited.add(current_file_path)

            if not os.path.exists(current_file_path):
                print(f"⚠️ [Flatten] 警告: 找不到导入文件 {current_file_path}")
                return f"// Error: Could not find {current_file_path}\\n"

            with open(current_file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 正则匹配 import "./Foo.sol"; 或 import "Foo.sol";
            # 简单起见，只处理双引号导入
            import_pattern = re.compile(r'import\s+"([^"]+)";')
            
            def replace_import(match):
                import_path = match.group(1)
                # 计算绝对路径
                dir_name = os.path.dirname(current_file_path)
                abs_import_path = os.path.normpath(os.path.join(dir_name, import_path))
                
                return f"// File: {import_path}\\n" + resolve_imports(abs_import_path, visited)

            return import_pattern.sub(replace_import, content)

        try:
            print(f"🔄 [System] 正在尝试扁平化合约: {file_path}")
            flattened = resolve_imports(os.path.abspath(file_path))
            return flattened
        except Exception as e:
            print(f"⚠️ [Flatten] 扁平化失败: {e}")
            return None

    def analyze(self, file_path: str, contract_code: str, mode: str = "SECURITY", user_intent: str = "", enable_poc: bool = False) -> AuditReport:
        
        # 1. 🚀 静态分析
        print(f"🔍 [System] 正在运行静态分析 (模式: {project_settings.PROJECT_TYPE})...")
        static_result = self.static_analyzer.run_analysis(file_path)
        print(f"✅ [System] 静态分析完成。")
        
        # 2. 📄 尝试扁平化 (解决 Dependency Hell)
        flattened_code = self._flatten_contract(file_path)
        if flattened_code:
            print("✅ [System] 合约扁平化成功。")
            code_to_analyze = flattened_code
        else:
            print("⚠️ [System] 未能扁平化合约 (或未安装工具)，将分析单文件。建议使用扁平化后的代码以获得最佳效果。")
            code_to_analyze = contract_code

        # 3. 📝 构建 Prompt & 动态 Schema
        schema_dict = self.report_schema.model_json_schema()
        
        # [优化] 如果未开启 PoC，直接从 JSON Schema 中移除该字段
        # 这样 LLM 就根本不知道这个字段的存在，从而节省 Token 和计算资源
        if not enable_poc:
            defs = schema_dict.get('$defs', {})
            if 'Vulnerability' in defs:
                props = defs['Vulnerability'].get('properties', {})
                if 'poc_code' in props:
                    del props['poc_code']

        schema_json = json.dumps(schema_dict, indent=2)
        
        if mode == "GAS":
            system_prompt = prompt_templates.GAS_OPTIMIZATION_SYSTEM_PROMPT
            user_prompt = prompt_templates.GAS_USER_PROMPT_TEMPLATE.format(
                contract_code=code_to_analyze,
                schema_json=schema_json
            )
        else:
            # SECURITY 模式
            poc_instruction = ""
            if enable_poc:
                poc_instruction = "5. **PoC 生成**：对于高危漏洞，请生成 Foundry (Solidity) 测试用例代码 (`poc_code` 字段)，证明漏洞可被利用。"
            
            system_prompt = prompt_templates.SYSTEM_PROMPT_TEMPLATE
            user_prompt = prompt_templates.USER_PROMPT_TEMPLATE.format(
                user_intent=user_intent if user_intent else "无特定业务意图描述。",
                rag_context=self.rag_context,
                static_analysis_result=static_result,  
                schema_json=schema_json,
                contract_code=code_to_analyze,
                poc_instruction=poc_instruction
            )

        print(f"🧠 [AI] 正在调用 {llm_settings.MODEL_NAME} 进行语义分析 (模式: {mode})...")
        
        # 4. 🤖 调用 LLM
        try:
            report_data = self.llm_service.generate_response(
                system_prompt=system_prompt,
                user_prompt=user_prompt
            )
            
            # 5. 🔍 解析结果
            # 服务层已经返回了字典，直接验证
            report = self.report_schema(**report_data)

            # [后处理] 如果未开启 PoC，强制清除 LLM 可能生成的 PoC 代码
            if not enable_poc:
                for vul in report.vulnerabilities:
                    vul.poc_code = None
            
            return report
            
        except (json.JSONDecodeError, ValidationError) as e:
            print(f"❌ 解析 LLM 响应失败: {e}")
            # 返回空报告或抛出异常
            return self.report_schema(vulnerabilities=[], analysis_summary="分析失败，无法解析模型输出。")
