# main.py
import argparse
import os
import sys
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

    return parser.parse_args()

def load_contract_code(file_path: str) -> str:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"❌ 错误: 找不到文件 '{file_path}'")
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

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
    print(f"🔧 审计模式: {detected_type}") # 打印当前模式
    
    try:
        # 2. [✨] 使用工厂组装依赖 (Dependency Injection)
        llm_service = ServiceFactory.get_llm_service()
        static_analyzer = ServiceFactory.get_static_analyzer()
        
        # 3. 大语言模型服务 + 注入分析器
        analyzer = AuditAnalyzer(llm_service=llm_service, static_analyzer=static_analyzer)

        # 4. 执行业务逻辑
        contract_code = load_contract_code(args.file)
        report = analyzer.analyze(file_path=args.file, contract_code=contract_code)
        
        print_report(report)

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