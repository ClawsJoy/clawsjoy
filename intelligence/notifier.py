"""智能通知器 - 重要事件通知"""
from datetime import datetime
from pathlib import Path
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

class Notifier:
    def __init__(self):
        self.notification_file = Path("logs/notifications.log")
        self.notification_file.parent.mkdir(exist_ok=True)
        
    def send(self, title, message, level='info'):
        """发送通知"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        icons = {'info': 'ℹ️', 'warning': '⚠️', 'success': '✅', 'error': '❌'}
        icon = icons.get(level, '📢')
        
        notification = f"[{timestamp}] {icon} {title}: {message}"
        print(notification)
        
        # 记录到文件
        with open(self.notification_file, 'a') as f:
            f.write(f"{datetime.now().isoformat()} | {level} | {title} | {message}\n")
        
        # 如果是严重问题，记录到大脑
        if level in ['warning', 'error']:
            from agent_core.brain_enhanced import brain
            brain.record_experience(
                agent="notifier",
                action=f"notification_{level}",
                result={"title": title, "message": message},
                context="system_alert"
            )
    
    def notify_service_status(self, service_name, status):
        """通知服务状态变化"""
        if status == 'healthy':
            self.send(f"{service_name} 服务正常", "运行中", 'success')
        elif status == 'unhealthy':
            self.send(f"{service_name} 服务异常", "需要检查", 'warning')
        elif status == 'down':
            self.send(f"{service_name} 服务停止", "正在尝试恢复", 'error')

if __name__ == "__main__":
    notifier = Notifier()
    notifier.send("系统测试", "智能通知器已启动", 'success')
