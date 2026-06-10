#!/bin/bash
# 一键初始化项目环境
set -e

cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv .venv
fi

echo "📥 安装依赖..."
.venv/bin/pip install -q -r requirements.txt

echo "✅ 环境就绪，使用方式："
echo "   .venv/bin/python test_server.py"
echo "   或先激活：source .venv/bin/activate"
