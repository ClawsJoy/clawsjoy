#!/bin/bash
echo "🔧 修复 Agent 核心问题"

# 1. 修复 Orchestrator 导入
cd /home/flybo/clawsjoy_v5
echo "修复 Orchestrator 类名..."

# 2. 添加自我介绍功能
echo "添加自我介绍功能..."
cat >> agents/chat_agent/agent.py << 'NEW'

    def _extract_name(self, user_input: str):
        """提取用户名字"""
        import re
        patterns = [
            r'我叫[\s]*([^\s，。！？]{2,4})',
            r'我是[\s]*([^\s，。！？]{2,4})',
            r'名字[叫是][\s]*([^\s，。！？]{2,4})',
        ]
        for pattern in patterns:
            match = re.search(pattern, user_input)
            if match:
                return match.group(1)
        return None
NEW

# 3. 重启服务
echo "重启服务..."
pkill -f gunicorn
sleep 2
./start_prod.sh

echo "✅ 修复完成"
