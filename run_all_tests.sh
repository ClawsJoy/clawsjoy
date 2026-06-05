#!/bin/bash
echo "🔬 ClawsJoy v5 内部核心功能综合验证"
echo "====================================="
echo "开始时间: $(date)"
echo ""

# 运行所有测试
echo ">>> 1. Agent 核心测试"
python3 test_agents_core.py 2>&1 | tail -30
echo ""

echo ">>> 2. 技能系统测试"
python3 test_skills_core.py 2>&1 | tail -30
echo ""

echo ">>> 3. 记忆系统测试"
python3 test_memory_core.py 2>&1 | tail -30
echo ""

echo ">>> 4. 引擎系统测试"
python3 test_engines_core.py 2>&1 | tail -30
echo ""

echo ">>> 5. 协作通信测试"
python3 test_collaboration.py 2>&1 | tail -30
echo ""

echo "====================================="
echo "验证完成时间: $(date)"
