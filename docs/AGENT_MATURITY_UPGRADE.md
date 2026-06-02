# Agent 成熟度升级指南

## 如何让现有 Agent 获得增强能力

### 方式1：继承 Mixin（推荐）

```python
from core.agents.base.smart_agent import SmartAgent
from core.agents.base.agent_maturity_mixin import MaturityMixin
from core.agents.base.config_helper_mixin import ConfigHelperMixin

class CodeAgent(SmartAgent, MaturityMixin, ConfigHelperMixin):
    # 无需修改现有代码，直接使用
    pass

# 使用 safe_process 替代 process
result = agent.safe_process(user_input)

###方式2：逐步迁移
#1.先添加 Mixin，不影响现有功能
#2.在测试环境中验证 safe_process
#3.确认无误后替换调用方
##配置示例
#在 config/agents/agent_defaults.yaml 中配置各 Agent 参数
