import yaml
import re

# 加载配置
with open("config/agents_config.yaml", 'r') as f:
    config = yaml.safe_load(f)

print("✅ 配置加载成功")
print(f"路由映射: {config['decision_agent']['routes']}")
print(f"关键词: {config['decision_agent']['keywords']}")
