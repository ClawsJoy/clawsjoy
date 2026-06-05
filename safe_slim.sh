#!/bin/bash
echo "=== 安全瘦身（只删除确定无影响的文件）==="

cd /home/flybo/clawsjoy_v5

# 1. 确认服务当前正常
echo "1. 检查服务状态..."
if curl -s http://127.0.0.1:5002/health > /dev/null; then
    echo "   ✅ 服务正常"
else
    echo "   ❌ 服务异常，停止瘦身"
    exit 1
fi

# 2. 只删除缓存和临时文件
echo -e "\n2. 删除缓存文件..."
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
echo "   ✅ 已删除"

# 3. 删除备份文件
echo -e "\n3. 删除备份文件..."
find . -name "*.backup*" -delete
find . -name "*.bak" -delete
find . -name "*.orig" -delete
echo "   ✅ 已删除"

# 4. 再次验证服务
echo -e "\n4. 验证服务仍正常..."
sleep 2
if curl -s http://127.0.0.1:5002/health > /dev/null; then
    echo "   ✅ 服务正常，瘦身安全"
else
    echo "   ❌ 服务异常"
fi

echo -e "\n✅ 安全瘦身完成"
