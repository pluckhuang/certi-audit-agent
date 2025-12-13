# config/prompt_templates.py

RAG_CONTEXT_TEMPLATE = "{best_practices_content}"

SYSTEM_PROMPT_TEMPLATE = (
    "你是一位经验丰富的区块链安全审计工程师。你的任务是分析智能合约代码，"
    "结合静态分析工具的发现，输出严格符合 JSON Schema 的审计报告。"
)

USER_PROMPT_TEMPLATE = """
    请严格根据以下步骤分析提供的代码：
    
    ### 步骤 1：上下文增强与事实核查
    
    **A. 安全最佳实践 (RAG):**
    {rag_context}
    
    **B. 静态代码分析报告 (工具运行结果):**
    *这是由确定性算法生成的分析结果。如果报告了漏洞，请务必在你的分析中包含它并解释其原理。*
    ---
    {static_analysis_result}
    ---
    
    ### 步骤 2：漏洞识别和推理 (混合分析)
    1. **结合分析**：确认静态分析报告的漏洞位置，结合代码上下文解释其成因。
    2. **语义补充**：利用大模型能力，寻找工具无法发现的逻辑漏洞（如权限控制、业务流程缺陷等等）。
    3. **修复生成**：为所有发现的漏洞生成修复代码。

    ### 步骤 3：结构化输出
    请将最终审计结果严格输出为以下 JSON Schema 格式。
    ---
    {schema_json}
    ---
    
    待分析的代码：
    ---
    {contract_code}
    ---
"""