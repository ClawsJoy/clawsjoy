#!/bin/bash
# 统一需求处理入口

echo "=========================================="
echo "ClawsJoy 需求处理器"
echo "=========================================="
echo "1. 用户任务（自动）"
echo "2. 管理员手动输入"
echo "3. 架构师建议"
echo "=========================================="
echo ""

read -p "请输入需求描述: " requirement

echo ""
echo "📝 处理中..."

python3 << PYEOF
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')
from skills.code_agent_v2 import skill

result = skill.execute({
    "requirement": "$requirement",
    "auto_register": True
})

if result.get('success'):
    print(f"\n✅ 技能已生成: {result.get('skill_name')}")
    print(f"   文件: skills/{result.get('skill_name')}.py")
else:
    print(f"\n❌ 失败: {result.get('error')}")
PYEOF
