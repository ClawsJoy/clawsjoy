"""定时调度器 - 让主动闭环定时运行"""

import threading
import time
from datetime import datetime
from pathlib import Path

import schedule


class AutonomousScheduler:
    """自主调度器"""

    def __init__(self):
        self.running = True
        self.log_file = Path(
            f"{config_helper.get_data_root()}/autonomous/scheduler.log"
        )
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def _log(self, msg: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {msg}"
        print(log_msg)
        with open(self.log_file, "a") as f:
            f.write(log_msg + "\n")

    def run_active_loop(self):
        """运行主动闭环"""
        try:
            from core.autonomous.active_closed_loop import active_loop

            result = active_loop.run_once()
            self._log(f"闭环完成: {result['decision'].get('action', 'idle')}")
        except Exception as e:
            self._log(f"闭环错误: {e}")

    def run_maintenance(self):
        """运行维护任务"""
        try:
            from core.lib.proactive_service import proactive

            result = proactive.run_maintenance()
            self._log(f"维护完成: 释放 {result['cache']['freed_bytes']} bytes")
        except Exception as e:
            self._log(f"维护错误: {e}")

    def run_report(self):
        """生成报告"""
        try:
            from core.lib.proactive_service import proactive

            report = proactive.generate_report()
            self._log(f"报告生成: {report.get('file', 'unknown')}")
        except Exception as e:
            self._log(f"报告错误: {e}")

    def start(self):
        """启动调度器"""
        # 每30秒执行主动闭环
        schedule.every(30).seconds.do(self.run_active_loop)

        # 每小时执行维护
        schedule.every().hour.do(self.run_maintenance)

        # 每6小时生成报告
        schedule.every(6).hours.do(self.run_report)

        self._log("调度器启动")
        self._log("  - 主动闭环: 每30秒")
        self._log("  - 系统维护: 每小时")
        self._log("  - 系统报告: 每6小时")

        while self.running:
            schedule.run_pending()
            time.sleep(1)

    def stop(self):
        self.running = False
        self._log("调度器停止")


scheduler = AutonomousScheduler()
