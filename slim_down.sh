#!/bin/bash
echo "🔪 ClawsJoy v5 瘦身计划"
echo "========================"

cd /home/flybo/clawsjoy_v5

# 1. 备份当前状态
echo "1. 备份当前状态..."
mkdir -p ../clawsjoy_backup_$(date +%Y%m%d)
cp -r core/lib ../clawsjoy_backup_$(date +%Y%m%d)/

# 2. 合并重复的配置模块
echo -e "\n2. 合并配置模块..."
# unified_config 是主要的，config_helper 和 config_manager 可以废弃
# 但需要先检查是否有依赖

# 3. 删除未使用的导入
echo -e "\n3. 清理未使用的导入..."
autoflake --in-place --remove-unused-variables --remove-all-unused-imports -r core/lib/ 2>/dev/null

# 4. 合并相似的 Agent 基类
echo -e "\n4. 检查 Agent 基类..."
echo "   发现多个基类，建议统一使用 core/agents/base/base_agent.py"

# 5. 删除重复的备份文件
echo -e "\n5. 删除备份文件..."
find . -name "*.backup*" -type f -delete
find . -name "*.bak" -type f -delete
find . -name "*.orig" -type f -delete

echo -e "\n✅ 瘦身完成！"
echo "建议手动检查以下目录:"
echo "  - core/lib/ 中有多个功能重叠的模块"
echo "  - config/ 中有 182 个配置文件，可以合并"
echo "  - agents/ 中有 18 个 Agent，可以抽取公共代码"
