# static_analyzers/slither_analyzer.py
import json
import subprocess
import shutil
import os
from static_analyzers.abstract_analyzer import AbstractStaticAnalyzer

class SlitherAnalyzer(AbstractStaticAnalyzer):
    """
    针对 EVM/Solidity 的分析器实现，底层使用 Slither
    """
    
    def check_installed(self) -> bool:
        return shutil.which("slither") is not None

    def run_analysis(self, file_path: str) -> str:
        if not self.check_installed():
            return "⚠️ 警告: 系统未检测到 'slither' 命令。"
        
        if not os.path.exists(file_path):
            return f"错误: 文件不存在 {file_path}"

        try:
            # 执行命令
            result = subprocess.run(
                ["slither", file_path, "--json", "-"],
                capture_output=True,
                text=True,
                check=False 
            )
            
            raw_output = result.stdout.strip()
            if not raw_output:
                 return f"Slither 未返回输出。Stderr: {result.stderr.strip()}"

            # 解析 JSON
            try:
                data = json.loads(raw_output)
            except json.JSONDecodeError:
                return f"Slither 输出非标准 JSON，跳过解析。\n片段: {raw_output[:200]}..."

            detectors = data.get("results", {}).get("detectors", [])
            
            if not detectors:
                return "✅ Slither 分析完成：未发现已知的高危漏洞模式。"

            # 构建摘要
            summary = ["### 🔍 Slither 静态分析报告 (EVM):"]
            for i, det in enumerate(detectors):
                check_id = det.get("check", "Unknown")
                description = det.get("description", "No description")
                impact = det.get("impact", "Unknown")
                
                lines = []
                if det.get("elements"):
                    for elem in det["elements"]:
                        if "source_mapping" in elem and "lines" in elem["source_mapping"]:
                            lines.extend(elem["source_mapping"]["lines"])
                
                line_str = f"Line {lines}" if lines else "Global"
                summary.append(f"{i+1}. [{impact}] **{check_id}** ({line_str})")
                summary.append(f"   - 详情: {description}")

            return "\n".join(summary)

        except Exception as e:
            return f"❌ Slither 分析器执行异常: {str(e)}"