# main.py
import argparse
import os
import sys
import json
from dotenv import load_dotenv

# 加载环境
load_dotenv()

from core.analyzer import AuditAnalyzer
from core.pydantic_schema import AuditReport
from core.factories import ServiceFactory
from config.settings import project_settings

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="Certi-Audit AI Agent: 基于 LLM 和静态分析的智能合约审计工具"
    )
    
    # 必须参数：目标文件
    parser.add_argument(
        "file", 
        type=str, 
        help="待审计的智能合约文件路径 (例如: contracts/Token.sol)"
    )
    
    # 可选参数：覆盖项目类型 (EVM, SOLANA)
    parser.add_argument(
        "--type", 
        type=str, 
        choices=["EVM", "SOLANA", "MOVE"],
        default=None,
        help="覆盖 .env 中的项目类型配置"
    )

    # [新增] 审计模式
    parser.add_argument(
        "--mode",
        type=str,
        choices=["SECURITY", "GAS"],
        default="SECURITY",
        help="审计模式: SECURITY (安全漏洞) 或 GAS (Gas 优化)"
    )

    # [新增] 用户意图描述
    parser.add_argument(
        "--desc",
        type=str,
        default="",
        help="合约业务逻辑的简短描述，用于辅助 AI 理解用户意图 (例如: '这是一个不可转让的灵魂绑定代币')"
    )

    # [新增] 是否开启 PoC 生成 (默认关闭以加快速度)
    parser.add_argument(
        "--poc",
        action="store_true",
        help="开启 PoC (Proof of Concept) 代码生成。注意：这会显著增加分析时间。"
    )

    # [新增] 输出格式
    parser.add_argument(
        "--output",
        type=str,
        choices=["CONSOLE", "JSON", "MARKDOWN"],
        default="CONSOLE",
        help="报告输出格式"
    )

    return parser.parse_args()

def load_contract_code(file_path: str) -> str:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"❌ 错误: 找不到文件 '{file_path}'")
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def save_report(report: AuditReport, output_format: str, file_path: str):
    """保存报告到文件"""
    if output_format == "JSON":
        output_file = "audit_report.json"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(report.model_dump_json(indent=2))
        print(f"\n💾 报告已保存至: {output_file}")
        
    elif output_format == "MARKDOWN":
        output_file = "audit_report.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"# 🛡️ 智能合约审计报告\n\n")
            f.write(f"**目标文件:** `{file_path}`\n\n")
            f.write(f"## 📊 摘要\n{report.analysis_summary}\n\n")
            f.write(f"## 🚨 详细发现\n")
            for i, vul in enumerate(report.vulnerabilities):
                f.write(f"### {i+1}. {vul.name} ({vul.severity})\n")
                f.write(f"- **位置:** Line {vul.line}\n")
                f.write(f"- **描述:** {vul.description}\n")
                f.write(f"- **修复建议:**\n```solidity\n{vul.fix_suggestion}\n```\n")
                if vul.poc_code:
                    f.write(f"- **PoC 测试用例:**\n```solidity\n{vul.poc_code}\n```\n")
                f.write("\n---\n")
        print(f"\n💾 报告已保存至: {output_file}")

def print_report(report: AuditReport):
    print("\n" + "="*70)
    print(f"✅ 审计报告生成完成")
    print("="*70)
    print(f"**摘要:** {report.analysis_summary}\n")

    if not report.vulnerabilities:
        print("🎉 代码很干净，未发现重大漏洞。")
        return

    for i, vul in enumerate(report.vulnerabilities):
        print(f"🔴 [漏洞 {i+1}] {vul.name} ({vul.severity})")
        print(f"   📍 位置: Line {vul.line}")
        print(f"   📝 描述: {vul.description}")
        print(f"   🛠️ 建议: {vul.fix_suggestion}")
        if vul.poc_code:
            print(f"   💣 PoC: (已生成测试用例，请查看完整报告)")
        print("-" * 30)

def detect_project_type(file_path: str, explicit_type: str = None) -> str:
    """
    智能推断项目类型
    优先级: 命令行参数 > 文件后缀 > 默认配置
    """
    if explicit_type:
        return explicit_type
        
    if file_path.endswith(".sol"):
        return "EVM"
    elif file_path.endswith(".rs"): # Rust 文件
        return "SOLANA"
    elif file_path.endswith(".move"): # Move 文件 (未来预留)
        return "MOVE"
        
    return "EVM" # 默认回退

def main():
    # 1. 解析参数
    args = parse_arguments()
    
    # [✨] 智能类型检测
    detected_type = detect_project_type(args.file, args.type)
    
    project_settings.PROJECT_TYPE = detected_type

    print(f"🚀 启动 Certi-Audit Agent...")
    print(f"📂 目标文件: {args.file}")
    print(f"🔧 审计模式: {detected_type} | 任务: {args.mode}") # 打印当前模式
    if args.desc:
        print(f"📝 业务意图: {args.desc}")
    
    try:
        # 2. [✨] 使用工厂组装依赖 (Dependency Injection)
        llm_service = ServiceFactory.get_llm_service()
        static_analyzer = ServiceFactory.get_static_analyzer()
        
        # 3. 大语言模型服务 + 注入分析器
        analyzer = AuditAnalyzer(llm_service=llm_service, static_analyzer=static_analyzer)

        # 4. 执行业务逻辑
        contract_code = load_contract_code(args.file)
        
        # [新增] 传入 mode 和 user_intent
        report = analyzer.analyze(
            file_path=args.file, 
            contract_code=contract_code,
            mode=args.mode,
            user_intent=args.desc,
            enable_poc=args.poc
        )
        
        # 5. 输出报告
        if args.output == "CONSOLE":
            print_report(report)
        else:
            save_report(report, args.output, args.file)

    except FileNotFoundError as e:
        print(e)
        sys.exit(1)
    except ValueError as e:
        print(f"❌ 配置错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 运行时发生未捕获异常: {e}")
        # 在开发阶段可以把下面这行打开看堆栈
        # import traceback; traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
