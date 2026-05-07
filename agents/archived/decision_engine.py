"""决策引擎 - 让 Agent 知道什么时候该做什么"""

class DecisionEngine:
    def __init__(self):
        self.rules = [
            {
                "condition": "disk_usage > 85",
                "action": "cleanup",
                "priority": 1,
                "description": "磁盘使用率超过85%，执行清理"
            },
            {
                "condition": "service_down == 'chat-api'",
                "action": "restart_chat_api",
                "priority": 2,
                "description": "Chat API 故障，尝试重启"
            },
            {
                "condition": "service_down == 'promo-api'",
                "action": "restart_promo_api",
                "priority": 2,
                "description": "Promo API 故障，尝试重启"
            },
            {
                "condition": "ollama_down == True",
                "action": "restart_ollama",
                "priority": 1,
                "description": "Ollama 服务停止，立即重启"
            },
            {
                "condition": "error_count > 10",
                "action": "send_alert",
                "priority": 3,
                "description": "错误日志超过10条，发送告警"
            }
        ]
    
    def decide(self, context):
        """根据当前状态做出决策"""
        actions = []
        for rule in self.rules:
            if self._evaluate(rule["condition"], context):
                actions.append({
                    "action": rule["action"],
                    "priority": rule["priority"],
                    "description": rule["description"]
                })
        return sorted(actions, key=lambda x: x["priority"])
    
    def _evaluate(self, condition, context):
        """评估条件"""
        try:
            return eval(condition, {"__builtins__": {}}, context)
        except:
            return False
