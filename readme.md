# 🛡️ Certi-Audit-Agent v1.0 (Multi-Chain Edition)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**基于混合引擎 (Hybrid Engine) 的多链智能合约安全审计平台**
*支持 Ethereum (EVM), Solana, 并已为 Sui (Move) 架构就绪*

---

## 📖 项目简介

**Certi-Audit-Agent** 是一个区块链安全审计工具。它突破了传统单一语言审计工具的限制，采用 **策略模式 (Strategy Pattern)** 构建了一个统一的安全分析框架。

本项目核心采用 **"Hybrid Analysis" (混合分析)** 机制：

- **静态分析层 (Fact Layer)**: 调用底层专用工具（Slither, Soteria 等）提取确定性漏洞事实。
- **语义分析层 (Reasoning Layer)**: 利用 LLM (GPT-4o/Gemini) 的语义理解能力，结合静态分析结果与 RAG 知识库，输出具备业务上下文的修复建议。

## 🌟 核心特性

- **🔌 多链架构 (Multi-Chain Architecture)**:
    - **EVM (Solidity)**: 完整集成 Slither，支持 AST/CFG 级深度分析。
    - **Solana (Rust)**: 集成 Soteria 适配器，支持 Account 验证与签名检查。
    - **Sui (Move)**: Architecture Ready. 已预留 Move Prover 扩展接口。

- **🏭 自动化工厂 (Auto-Factory)**:
    - 基于文件后缀 (`.sol`, `.rs`, `.move`) 智能识别项目类型。
    - 通过依赖注入 (DI) 自动装配对应的分析器策略，无需修改核心代码。

- **🧠 混合动力引擎**: 将冷冰冰的代码报错转化为人类可读的、包含修复代码的结构化报告。

- **🛡️ 工程化落地**: 严格的 Pydantic Schema 校验、错误降级处理 (Graceful Degradation)、环境隔离配置。

## 🏗️ 系统架构

采用了经典的 **策略模式** 与 **抽象工厂模式**，实现核心逻辑与底层工具链的解耦。

```mermaid
graph TD
    User[用户 / CI Pipeline] --> Main[CLI 入口]
    Main -- "1. 识别文件类型" --> Factory[Service Factory]
    
    subgraph "Core Business Logic"
        Factory -- "2. 组装组件" --> Analyzer[Audit Analyzer]
        Analyzer --> LLM_Interface[Abstract LLM Service]
        Analyzer --> Static_Interface[Abstract Static Analyzer]
    end
    
    subgraph "Static Analysis Strategies"
        Static_Interface -- "EVM Mode" --> Slither[Slither Adapter]
        Static_Interface -- "Solana Mode" --> Soteria[Soteria Adapter]
        Static_Interface -. "Sui Mode (Reserved)" .-> SuiMove[Sui Move Adapter]
    end
    
    subgraph "External Tools"
        Slither --> Binary1[slither-cli]
        Soteria --> Binary2[soteria-cli]
        SuiMove -.-> Binary3[sui-move-analyzer]
    end

    Analyzer -- "3. 生成报告" --> Report[JSON/Markdown Report]
```

## 📂 项目结构

```plaintext
Certi-Audit-Agent/
├── config/                 # [配置层]
│   ├── settings.py         # 支持 PROJECT_TYPE 动态切换
│   └── ...
├── core/                   # [业务层]
│   ├── factories.py        # [工厂] 负责 LLM 和 Analyzer 的装配
│   ├── analyzer.py         # [核心] 审计编排器 (依赖抽象接口)
│   └── ...
├── static_analyzers/       # [策略层] 核心解耦点
│   ├── abstract_analyzer.py# 定义标准分析行为 (Interface)
│   ├── slither_analyzer.py # EVM 实现
│   ├── soteria_analyzer.py # Solana 实现
│   └── sui_analyzer.py     # [TODO] Sui/Move 预留扩展
├── llm_services/           # [模型层]
│   ├── openai_service.py
│   └── gemini_service.py
├── main.py                 # [入口] 智能参数解析
└── requirements.txt
```

## 🚀 快速开始

### 1. 基础环境

- Python 3.10+
- Solc-select (EVM 必须)
- Rust Toolchain (Solana/Sui 必须)

### 2. 安装步骤 (按需)

```bash
# 1. 克隆项目
cd certi-audit-agent

# 2. 创建并激活虚拟环境 (推荐)
python3 -m venv venv
source venv/bin/activate  # Windows 用户使用: venv\Scripts\activate

# 3. 安装 Python 依赖
pip install -r requirements.txt

# [EVM] 安装 Slither
pip install slither-analyzer

# [Solana] 安装 Soteria (Linux/Mac)
sh -c "$(curl -k https://supercompiler.xyz/install)"

检测 Eth 合约需要配置 Solidity 编译器 (关键)
项目依赖 Slither 进行静态分析，Slither 需要与合约版本匹配的 solc 编译器。

# 安装 solc 版本管理工具 (如果 requirements.txt 中已安装，可跳过此行)
pip install solc-select

# 安装目标合约所需的编译器版本 (以 0.8.0 为例，对应 VulnerableToken.sol)
solc-select install 0.8.0

# 切换并激活该版本
solc-select use 0.8.0

如果计划审计 Solana 合约：

# 安装 Rust 工具链
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# 安装 Soteria 分析器
sh -c "$(curl -k https://supercompiler.xyz/install)"

```

### 3. 配置

复制 `.env.example` 为 `.env` 并填入 API Key。

```ini
# LLM 配置
LLM_MODEL_NAME=gemini-2.5-flash
# 自动检测，也可强制指定: EVM, SOLANA, SUI
PROJECT_TYPE=EVM 
```

## 🛠️ 使用指南

### 场景 A：审计 Ethereum 合约

系统自动识别 `.sol` 后缀，加载 `SlitherAnalyzer`。

```bash
python main.py contracts/VulnerableToken.sol
```

### 场景 B：审计 Solana 程序

系统自动识别 `.rs` 后缀，加载 `SoteriaAnalyzer`。

```bash
python main.py programs/my_program/src/lib.rs
```

### 场景 C：扩展 Sui (Move) 支持

虽然代码尚未完全实现，但可以通过命令行强制指定类型（需先实现适配器）。

```bash
python main.py sources/coin.move --type SUI
```

## 🔮 扩展指南：如何添加 Sui 支持？

由于本项目严格遵循 **开闭原则 (OCP)**，添加 Sui 支持无需修改核心逻辑，仅需三步：

1.  **实现适配器**： 在 `static_analyzers/` 下新建 `sui_analyzer.py`，继承 `AbstractStaticAnalyzer`，实现对 `sui move test` 或 `move-prover` 的调用。
2.  **注册工厂**： 在 `core/factories.py` 的 `_ANALYZER_REGISTRY` 中添加映射：
    ```python
    "SUI": SuiAnalyzer
    ```
3.  **更新知识库**： 在 `config/best_practices.txt` 中添加 Move 语言特有的 Object Ownership 安全原则。

## 📊 输出示例

```text
python main.py target_contracts/evm/VulnerableToken.sol
🚀 启动 Certi-Audit Agent...
📂 目标文件: target_contracts/evm/VulnerableToken.sol
🔧 审计模式: EVM
🏭 Factory: 根据模型名 'gemini-2.5-flash' 加载 -> create_gemini_service
🏭 Factory: 根据项目类型 'EVM' 加载 -> SlitherAnalyzer
🔍 [System] 正在运行静态分析 (模式: EVM)...
✅ [System] 静态分析完成。
   (摘要: ### 🔍 Slither 静态分析报告 (EVM): 1. [High] **reentrancy...)
🧠 [AI] 正在调用 gemini-2.5-flash 进行语义分析...

======================================================================
✅ 审计报告生成完成
======================================================================
**摘要:** 本次审计发现 `VulnerableToken` 合约存在一个高危的重入漏洞，主要原因是其 `withdraw` 函数未能遵循 Checks-Effects-Interactions (CEI) 安全模式。此外，合约使用了范围较广的 Solidity 编译器版本，存在低级调用，以及一个命名规范问题。作为语义补充，合约还缺少一个紧急暂停机制，这对于金融类合约而言是一个重要的安全最佳实践。

🔴 [漏洞 1] 重入漏洞 (Reentrancy) (High)
   📍 位置: Line 17
   📝 描述: 在 `withdraw` 函数中，外部调用 `msg.sender.call{value: _amount}("")` 发生在状态变量 `balances[msg.sender]` 更新之前。这违反了 Checks-Effects-Interactions (CEI) 模式。恶意合约可以利用此漏洞，在第一次提款的 Ether 到账后，立即再次调用 `withdraw` 函数，此时 `balances[msg.sender]` 尚未减少，导致攻击者可以多次提款，耗尽合约资金。
   🛠️ 建议: 严格遵循 Checks-Effects-Interactions (CEI) 模式。在进行任何外部调用之前，先更新合约的状态变量。或者，使用 ReentrancyGuard 模式来防止重入。
------------------------------
🔴 [漏洞 2] Solidity 编译器版本过旧/范围过广 (Informational)
   📍 位置: Line 2
   📝 描述: 合约使用了 `^0.8.0` 的编译器版本约束。这意味着合约可能使用任何 `0.8.x` 版本的编译器进行编译。某些旧的 `0.8.x` 版本已知存在编译器错误，可能导致意外行为或安全漏洞。建议锁定到一个特定的、经过充分测试的最新稳定版本。
   🛠️ 建议: 将 Solidity 编译器版本锁定到一个特定的、最新的稳定版本，例如 `0.8.20` 或更高版本，以避免潜在的编译器错误。
------------------------------
🔴 [漏洞 3] 缺少紧急暂停机制 (Medium)
   📍 位置: Line 17
   📝 描述: 合约缺乏一个紧急暂停机制，无法在发现漏洞或遭受攻击时暂停关键操作（如提款）。这可能导致在紧急情况下无法阻止资金流失，造成不可逆的损失。
   🛠️ 建议: 引入一个 `paused` 状态变量和一个仅限所有者调用的 `togglePause` 函数。在敏感函数（如 `withdraw`）中添加 `require(!paused, "Contract is paused")` 检查，以便在必要时暂停合约功能。
------------------------------
🔴 [漏洞 4] 低级调用 (Low-Level Call) (Informational)
   📍 位置: Line 22
   📝 描述: 在 `withdraw` 函数中使用了 `msg.sender.call{value: _amount}("")` 这种低级调用。低级调用虽然灵活，但绕过了 Solidity 的一些类型安全检查，如果使用不当，可能引入额外的复杂性和风险。在本合约中，它直接导致了重入漏洞。
   🛠️ 建议: 确保所有低级调用都经过严格的安全审查，并遵循 Checks-Effects-Interactions (CEI) 模式。对于简单的 Ether 转移，如果 gas 限制允许，可以考虑使用 `transfer()` 或 `send()`，它们提供了内置的重入保护（尽管有固定的 gas 限制）。
------------------------------
🔴 [漏洞 5] 命名规范违规 (Naming Convention Violation) (Informational)
   📍 位置: Line 17
   📝 描述: 在 `withdraw` 函数中，参数 `_amount` 的命名不符合 Solidity 推荐的 `mixedCase` 命名规范。虽然使用下划线前缀表示参数很常见，但 Slither 建议参数也应遵循 `mixedCase`。
   🛠️ 建议: 将参数 `_amount` 重命名为 `amount`，以符合 Solidity 的命名规范。
```
