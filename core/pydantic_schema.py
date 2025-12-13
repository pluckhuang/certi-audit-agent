# core/pydantic_schema.py
from pydantic import BaseModel, Field, conlist
from typing import Literal

from config.settings import llm_settings 

# 使用配置中的风险等级
SeverityType = Literal['High', 'Medium', 'Low', 'Informational']

class Vulnerability(BaseModel):
    """定义单个智能合约漏洞的结构化输出"""
    name: str = Field(description="漏洞的通用名称，例如 'Reentrancy'")
    line: int = Field(description="发现漏洞的起始行号")
    severity: SeverityType = Field(description="风险等级，必须在 High, Medium, Low, Informational 之一")
    description: str = Field(description="详细的技术描述和潜在的攻击向量")
    fix_suggestion: str = Field(description="简明扼要的修复策略，例如 '使用 Checks-Effects-Interactions 模式'")
    fixed_code_snippet: str = Field(description="修复后的代码段（不超过10行）")

class AuditReport(BaseModel):
    """定义最终的安全审计报告结构"""
    analysis_summary: str = Field(description="本次审计的总体摘要。")
    vulnerabilities: conlist(Vulnerability, min_length=0)