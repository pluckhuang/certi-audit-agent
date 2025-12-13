# static_analyzers/soteria_analyzer.py
import subprocess
import shutil
import os
from static_analyzers.abstract_analyzer import AbstractStaticAnalyzer

class SoteriaAnalyzer(AbstractStaticAnalyzer):
    """
    针对 Solana/Rust 的分析器实现，底层使用 Soteria
    """
    
    def check_installed(self) -> bool:
        # 检查 soteria 命令是否存在
        return shutil.which("soteria") is not None

    def run_analysis(self, file_path: str) -> str:
        """
        运行 Soteria 分析。
        注意：Soteria 通常在项目根目录运行，而不是针对单个文件。
        我们会尝试从 file_path 推断项目根目录。
        """
        if not self.check_installed():
            return "⚠️ 警告: 系统未检测到 'soteria' 命令。请参考 Veridise 文档安装 Soteria。"
        
        # 推断项目目录：假设 file_path 是 src/lib.rs，我们需要向上找 Cargo.toml
        abs_path = os.path.abspath(file_path)
        project_dir = os.path.dirname(abs_path)
        
        # 简单的向上查找 Cargo.toml 的逻辑 (最多找3层)
        for _ in range(3):
            if os.path.exists(os.path.join(project_dir, "Cargo.toml")):
                break
            project_dir = os.path.dirname(project_dir)
        else:
            # 如果找不到 Cargo.toml，就默认在文件所在目录跑
            project_dir = os.path.dirname(abs_path)

        try:
            # 执行命令: soteria . (在项目目录下)
            # Soteria 的输出通常是文本格式，不是 JSON，我们需要捕获 stdout
            result = subprocess.run(
                ["soteria", "."],
                cwd=project_dir, # 切换工作目录
                capture_output=True,
                text=True,
                check=False 
            )
            
            raw_output = result.stdout.strip()
            stderr_output = result.stderr.strip()
            
            # Soteria 如果没发现漏洞，通常输出包含 "No vulnerabilities found"
            if "No vulnerabilities found" in raw_output:
                return "✅ Soteria 分析完成：未发现已知的高危漏洞模式。"
            
            # 如果输出为空但有报错
            if not raw_output and stderr_output:
                return f"Soteria 运行出错 (Stderr): {stderr_output[:300]}..."

            # 截取关键输出 (Soteria 输出可能很长，只取前 2000 字符给 LLM)
            # 这里的清洗逻辑可以根据 Soteria 实际输出格式精修
            summary = [
                "### 🔍 Soteria 静态分析报告 (Solana):",
                "注意：以下是工具扫描的原始日志，请重点关注 'VULNERABILITY' 关键词。",
                "---"
            ]
            
            # 简单的日志清洗，去除进度条等噪音
            lines = raw_output.split('\n')
            relevant_lines = [line for line in lines if "Checking" not in line and "Compiling" not in line]
            
            # 限制长度以防爆 Token
            content_str = "\n".join(relevant_lines)
            if len(content_str) > 2000:
                content_str = content_str[:2000] + "\n...(输出截断)..."
                
            summary.append(content_str)

            return "\n".join(summary)

        except Exception as e:
            return f"❌ Soteria 分析器执行异常: {str(e)}"