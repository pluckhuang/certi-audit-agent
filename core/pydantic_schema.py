from pydantic import BaseModel, Field
from typing import List, Optional, Literal

# 扩展 SeverityType 以包含 Gas 优化和通用优化建议
SeverityType = Literal['High', 'Medium', 'Low', 'Informational', 'Gas', 'Optimization', 'Critical']

class Vulnerability(BaseModel):
    """定义单个智能合约漏洞的结构化输出"""
    name: str = Field(description="漏洞的通用名称，例如 'Reentrancy'")
    line: int = Field(description="发现漏洞的起始行号")
    severity: SeverityType = Field(description="风险等级")
    description: str = Field(description="详细的技术描述和潜在的攻击向量")
    fix_suggestion: str = Field(description="简明扼要的修复策略")
    fixed_code_snippet: str = Field(description="修复后的代码段")
    poc_code: Optional[str] = Field(None, description="[新增] Foundry/Hardhat 测试用例代码，用于复现漏洞")

class AuditReport(BaseModel):
    """定义最终的安全审计报告结构"""
    vulnerabilities: List[Vulnerability] = Field(description="发现的所有漏洞列表")
    analysis_summary: str = Field(description="对合约整体安全性的高层总结")
