#!/bin/bash

echo "🚀 开始初始化 Certi-Audit-Agent 环境..."

# 1. 安装 Python 依赖
echo "📦 正在安装 Python 依赖..."
pip install -r requirements.txt

# 2. 检查并配置 solc
echo "🔧 配置 Solidity 编译器..."
if ! command -v solc-select &> /dev/null; then
    echo "安装 solc-select..."
    pip install solc-select
fi

# 获取 VulnerableToken.sol 中定义的版本 (这里硬编码演示，实际可正则提取)
TARGET_SOLC_VERSION="0.8.0"

echo "正在安装 solc v$TARGET_SOLC_VERSION..."
solc-select install $TARGET_SOLC_VERSION
solc-select use $TARGET_SOLC_VERSION

# 3. 检查 Slither
if command -v slither &> /dev/null; then
    echo "✅ Slither 安装成功!"
else
    echo "❌ Slither 安装失败，请检查 PATH."
fi

echo "🎉 环境初始化完成! 请运行: python main.py target_contracts/evm/VulnerableToken.sol"