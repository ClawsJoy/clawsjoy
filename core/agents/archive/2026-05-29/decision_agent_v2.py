from core.lib.config_helper import get_data_root, get_llm_endpoint, get_llm_model, get_embedding_model, get_gateway_port, get_timeout
"""决策 Agent v4 - 集成主动服务"""

import json
import subprocess
import threading
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from core.lib.unified_config import unified_config
from core.lib.file_exchange import file_exchange
from core.lib.smart_active_service import SmartActiveService


class DecisionAgentV4:
    """决策 Agent v4 - 智能决策 + 主动服务"""

    VERSION = "4.0.0"

    def __init__(self):
        self.smart_service = SmartActiveService()
        self.running = False
        self.last_health_score = 85
        self.last_suggestions = []
        print(f"🧠 决策 Agent v{self.VERSION} 已启动")
        print("   集成主动服务模块")

    def start(self):
        """启动决策循环"""
        self.running = True
        thread = threading.Thread(target=self._run, daemon=True)
        thread.start()
        print("✅ 决策循环已启动")

    def _run(self):
        """主循环 - 监听分析结果"""
        while self.running:
            try:
                # 1. 接收分析报告
                message = file_exchange.receive("decision")
                if message:
                    self._process_analysis(message)
                
                # 2. 主动服务检查（每小时）
                if self._should_check_active():
                    self._check_active_services()
                
                time.sleep(5)
            except Exception as e:
                print(f"决策循环错误: {e}")
                time.sleep(10)

    def _process_analysis(self, message: Dict):
        """处理分析报告"""
        action = message.get("action")
        from_agent = message.get("from")

        print(f"\n📊 [{datetime.now().isoformat()}] 收到分析报告 from {from_agent}")

        if action == "analysis_report":
            health_score = message.get("health_score", 0)
            suggestions = message.get("suggestions", [])
            self.last_health_score = health_score
            self.last_suggestions = suggestions

            # 根据健康度决策
            if health_score < 50:
                self._handle_critical(health_score, suggestions)
            elif health_score < 70:
                self._handle_warning(health_score, suggestions)
            else:
                self._handle_healthy(health_score, suggestions)

            # 触发主动服务
            self._trigger_active_services(health_score)

    def _handle_critical(self, health_score: int, suggestions: list):
        """处理严重问题"""
        print(f"🚨 [严重] 健康度 {health_score}，需要紧急处理")

        # 执行修复动作
        actions = [
            ("重启网关", "sudo systemctl restart clawsjoy"),
            ("清理缓存", self._clear_cache),
            ("检查服务", self._check_services),
        ]

        for name, action in actions:
            print(f"  执行: {name}")
            if callable(action):
                action()
            else:
                subprocess.run(action, shell=True, capture_output=True)

    def _handle_warning(self, health_score: int, suggestions: list):
        """处理警告问题"""
        print(f"⚠️ [警告] 健康度 {health_score}，建议优化")

        for sug in suggestions[:3]:
            print(f"  建议: {sug.get('message', sug)}")

    def _handle_healthy(self, health_score: int, suggestions: list):
        """健康状态"""
        print(f"✅ [健康] 健康度 {health_score}，系统运行正常")

    def _trigger_active_services(self, health_score: int):
        """触发主动服务"""
        context = {
            "health_score": health_score,
            "task_completed": False,
            "error_detected": health_score < 70,
            "first_interaction": False
        }

        result = self.smart_service.should_serve("decision_agent", context)
        if result.get("should"):
            print(f"💡 主动服务触发: {result.get('reason')} (优先级: {result.get('priority')})")
            self._execute_service_action(result)

    def _execute_service_action(self, service_result: Dict):
        """执行主动服务动作"""
        reason = service_result.get("reason")

        if reason == "help_needed":
            print("  🆘 发送帮助通知")
            self._send_notification("系统需要帮助", "健康度下降")
        elif reason == "todo_reminder":
            print("  📋 检查待办提醒")
        elif reason == "morning_greeting":
            print("  🌅 发送早安问候")

    def _check_active_services(self):
        """定期检查主动服务"""
        self.last_check_time = datetime.now()
        # 可扩展更多主动服务检查

    def _should_check_active(self):
        """检查是否需要主动服务（每小时一次）"""
        if not hasattr(self, '_last_active_check'):
            self._last_active_check = datetime.now()
            return True
        hour_passed = (datetime.now() - self._last_active_check).seconds >= 3600
        if hour_passed:
            self._last_active_check = datetime.now()
        return hour_passed

    def _clear_cache(self):
        """清理缓存"""
        import shutil
        cache_dirs = [f"{get_data_root()}/temp_sessions", f"{get_data_root()}/__pycache__"]
        for d in cache_dirs:
            path = Path(d)
            if path.exists():
                shutil.rmtree(path)
                path.mkdir()
                print(f"    清理: {d}")

    def _check_services(self):
        """检查服务状态"""
        services = ["ollama", "gunicorn"]
        for svc in services:
            result = subprocess.run(f"pgrep -f {svc}", shell=True, capture_output=True)
            status = "运行中" if result.returncode == 0 else "停止"
            print(f"    {svc}: {status}")

    def _send_notification(self, title: str, message: str):
        """发送通知"""
        try:
            import requests
            webhook = unified_config.get("notification.webhook.url", "")
            if webhook:
                requests.post(webhook, json={"title": title, "message": message, "level": "warning"})
        except Exception as e:
            print(f"    通知发送失败: {e}")

    def stop(self):
        self.running = False


decision_agent = DecisionAgentV4()
