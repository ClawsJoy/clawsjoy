#!/bin/bash
# ClawsJoy 测试运行脚本

echo "🦞 ClawsJoy 测试套件"
echo "===================="

cd /home/flybo/clawsjoy

# 安装测试依赖
echo "📦 安装测试依赖..."
pip3 install pytest pytest-cov pytest-xdist pytest-timeout --break-system-packages

# 运行单元测试
echo ""
echo "🧪 运行单元测试..."
pytest tests/unit/ -v --tb=short

# 运行集成测试
echo ""
echo "🔗 运行集成测试..."
pytest tests/integration/ -v --tb=short

# 生成覆盖率报告
echo ""
echo "📊 生成覆盖率报告..."
pytest tests/ --cov=bin --cov-report=html --cov-report=term

echo ""
echo "✅ 测试完成"
echo "📁 覆盖率报告: /home/flybo/clawsjoy/htmlcov/index.html"
