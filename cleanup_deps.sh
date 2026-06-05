#!/bin/bash
echo "=== 分析未使用的依赖 ==="

# 检查是否真的未使用
UNUSED_PACKAGES=(
    "aio-pika"
    "aioboto3"
    "alembic"
    "alibabacloud-dypnsapi20170525"
    "amqp"
)

for pkg in "${UNUSED_PACKAGES[@]}"; do
    echo "检查: $pkg"
    if pip show "$pkg" &>/dev/null; then
        echo "  移除: $pkg"
        pip uninstall -y "$pkg"
    fi
done

echo "=== 清理完成 ==="
# 显示当前包数量
pip list | wc -l
