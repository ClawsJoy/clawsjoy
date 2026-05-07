#!/bin/bash
# 工程师专属学习：系统运维

echo "🔧 工程师学习系统运维..."
# 采集系统状态
ss -tlnp > /tmp/engineer_ports.txt
pm2 list > /tmp/engineer_services.txt
docker ps > /tmp/engineer_containers.txt

python3 -c "
from agents.learning_agent import LearningAgent
agent = LearningAgent()
agent.learn_domain('engineering', {
    'ports': open('/tmp/engineer_ports.txt').read(),
    'services': open('/tmp/engineer_services.txt').read(),
    'containers': open('/tmp/engineer_containers.txt').read()
})
"
