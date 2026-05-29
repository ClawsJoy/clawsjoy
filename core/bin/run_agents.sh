#!/bin/bash
# 运行所有 Agent 日常维护

echo "🦞 ClawsJoy Agent 日常维护"
echo "=========================="

# 1. 工程师检查
echo "🔧 工程师检查..."
python3 -c "
from agents.engineer_agent import EngineerAgent
e = EngineerAgent()
e.run_health_check()
"

# 2. 自愈修复
echo ""
echo "🩺 自愈检查..."
python3 -c "
from agents.self_healing import SelfHealingAgent
h = SelfHealingAgent()
# 读取错误日志
import subprocess
result = subprocess.run(['pm2', 'logs', '--lines', '20', '--nostream'], capture_output=True, text=True)
fixes = h.heal(result.stderr)
print(f'应用了 {len(fixes)} 个修复')
"

# 3. 清理检查
echo ""
echo "🧹 清理检查..."
python3 -c "
from agents.cleaner_agent import CleanerAgent
c = CleanerAgent()
c.scan_disk()
print('磁盘扫描完成')
"

echo ""
echo "✅ 日常维护完成"
