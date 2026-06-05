#!/bin/bash
echo "=========================================="
echo "运行核心模块测试"
echo "=========================================="

# 运行决策层测试
python3 -m pytest tests/ -v 2>/dev/null || python3 tests/test_decision_agent.py

echo ""
echo "✅ 测试完成"
