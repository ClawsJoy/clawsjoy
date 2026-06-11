import re

file_path = "agents/vision_agent/agent.py"

with open(file_path, 'r') as f:
    content = f.read()

# 修复 BusinessAgent 为 BusinessAgentV2
content = content.replace("class VisionAgent(BusinessAgent):", "class VisionAgent(BusinessAgentV2):")
content = content.replace("from core.agents.business.base_business_agent import BusinessAgent", 
                          "from core.agents.business.business_agent_v2 import BusinessAgentV2")

with open(file_path, 'w') as f:
    f.write(content)

print("✅ vision_agent 已修复")
