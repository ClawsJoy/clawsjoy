#!/bin/bash
echo "🔍 预览要删除的文件："
git clean -n
echo ""
read -p "确认删除？(y/N): " confirm
if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
    git clean -f
    echo "✅ 已清理"
else
    echo "❌ 取消清理"
fi
