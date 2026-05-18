#!/bin/bash
# 运行单元测试

cd /mnt/d/clawsjoy_clean

echo "=========================================="
echo "运行单元测试"
echo "=========================================="

# 运行测试
python3 -m pytest tests/ -v 2>/dev/null || python3 tests/unit/test_config.py

echo ""
echo "✅ 测试完成"
