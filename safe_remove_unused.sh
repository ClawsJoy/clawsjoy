#!/bin/bash
echo "🔧 安全清理未使用模块"
echo "========================"

cd /home/flybo/clawsjoy_v5

# 1. 创建备份目录
BACKUP_DIR="../clawsjoy_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
echo "备份目录: $BACKUP_DIR"

# 2. 分析结果提示
echo ""
echo "⚠️ 请先确认以下模块确实未被使用:"
echo "   1. 查看 analyze_usage.py 的输出"
echo "   2. 查看 coverage 报告"
echo "   3. 手动确认后，取消注释下面的删除命令"
echo ""
echo "示例删除命令:"
echo "   # mv core/lib/xxx.py $BACKUP_DIR/"
echo "   # mv core/lib/yyy.py $BACKUP_DIR/"

# 3. 列出可能未使用的模块（基于分析）
echo ""
echo "可能未使用的模块（仅供参考）:"
grep -l "可能未使用" analyze_usage.py 2>/dev/null || echo "请先运行 analyze_usage.py"
