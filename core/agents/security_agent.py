#!/usr/bin/env python3
"""安全 Agent - 独立的监控和监督角色"""

import time
from typing import Dict, Any, Optional

from core.agent.base import BaseAgent
from lib.file_exchange import file_exchange
from lib.security_hook import security_hook


class SecurityAgent(BaseAgent):
    """安全 Agent - 监控所有操作"""
    
    VERSION = "1.0.0"
    
    def __init__(self):
        super().__init__("SecurityAgent")
        self.alert_threshold = 5  # 告警阈值
        self.violation_count = 0
        self.log(f"安全 Agent 初始化完成")
    
    def process(self, user_input: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """处理请求"""
        # 安全检查
        safe, reason = security_hook.check(user_input)
        
        if not safe:
            self.violation_count += 1
            self.log(f"🚨 检测到违规: {reason}")
            
            if self.violation_count >= self.alert_threshold:
                self._send_alert(reason)
            
            return {
                "success": False,
                "error": "security_violation",
                "message": reason
            }
        
        return {"success": True, "message": "安全检查通过"}
    
    def _send_alert(self, reason: str):
        """发送告警"""
        self.log(f"🔔 告警! 已达到阈值, 最近违规: {reason}")
        # 可扩展：发送邮件、webhook 等
    
    def supervise(self, message: Dict) -> Tuple[bool, Optional[Dict]]:
        """监督消息"""
        return security_hook.check_message(message)
    
    def get_status(self) -> Dict:
        """获取状态"""
        return {
            "version": self.VERSION,
            "violation_count": self.violation_count,
            "alert_threshold": self.alert_threshold,
            "stats": security_hook.get_stats()
        }


security_agent = SecurityAgent()


if __name__ == "__main__":
    print(f"安全 Agent v{security_agent.VERSION}")
    
    # 测试
    result = security_agent.process("我想要漫剧人物")
    print(f"正常输入: {result}")
    
    # 测试安全拦截（如果有敏感词配置）
    # result = security_agent.process("敏感词测试")
    # print(f"敏感输入: {result}")
    
    print(f"\n状态: {security_agent.get_status()}")
