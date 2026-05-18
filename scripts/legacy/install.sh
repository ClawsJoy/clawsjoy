#!/bin/bash
# ClawsJoy 安装脚本

set -e

echo "=========================================="
echo "ClawsJoy 3.0 安装程序"
echo "=========================================="

# 检查 Python 版本
echo ""
echo "检查 Python 版本..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "✅ Python $PYTHON_VERSION"

# 安装依赖
echo ""
echo "安装 Python 依赖..."
pip install -r requirements.txt -q 2>/dev/null || pip install -r requirements.txt

# 创建配置文件
echo ""
echo "创建配置文件..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ 已创建 .env（请编辑配置）"
else
    echo "⚠️ .env 已存在"
fi

if [ ! -f config/config.yaml ]; then
    cp config/config.yaml.example config/config.yaml
    echo "✅ 已创建 config/config.yaml"
fi

# 创建数据目录
echo ""
echo "创建数据目录..."
mkdir -p data logs output

echo ""
echo "=========================================="
echo "✅ ClawsJoy 安装完成"
echo "=========================================="
echo ""
echo "下一步:"
echo "  1. 编辑 .env 配置文件"
echo "  2. 启动 Ollama: ollama serve"
echo "  3. 启动服务: ./start_all.sh"
echo ""
