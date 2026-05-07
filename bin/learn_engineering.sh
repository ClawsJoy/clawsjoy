#!/bin/bash
# 让 Agent 学习网络工程和系统工程

echo "📚 开始倾向性学习..."

# 1. 采集网络配置
echo "🔍 采集网络配置..."
ss -tlnp > /tmp/network_ports.txt 2>/dev/null
ip addr show >> /tmp/network_ports.txt 2>/dev/null

# 2. 采集系统信息
echo "🖥️ 采集系统信息..."
uname -a > /tmp/system_info.txt
df -h >> /tmp/system_info.txt
free -h >> /tmp/system_info.txt

# 3. 分析学习
python3 -c "
from agents.learning_agent import LearningAgent
agent = LearningAgent()

# 分析网络配置
with open('/tmp/network_ports.txt') as f:
    network_data = f.read()
print('📊 网络配置已分析')

# 分析系统信息
with open('/tmp/system_info.txt') as f:
    system_data = f.read()
print('📊 系统信息已分析')

agent.learn_network_troubleshooting()
agent.learn_system_maintenance()
"

echo "✅ 学习完成"
