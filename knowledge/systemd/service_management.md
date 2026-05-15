# Systemd 服务管理

## 核心概念
- systemd 是 Linux 系统的 init 系统
- 单元文件位置: /etc/systemd/system/
- 常用命令:
  - systemctl start/stop/restart/status <service>
  - journalctl -u <service> -f  # 查看日志

## WSL 环境特性
- WSL 不使用 systemd，使用 service 命令
- service docker start/stop/restart
- 进程管理用 pm2 代替 systemd
