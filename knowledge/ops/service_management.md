# 服务管理知识

## PM2 命令
- `pm2 list` - 查看所有服务状态
- `pm2 start <script> --name <name>` - 启动服务
- `pm2 restart <name>` - 重启服务
- `pm2 logs <name>` - 查看日志

## 常见问题
1. ModuleNotFoundError: 检查 Python 路径，使用 `from agents.xxx import`
2. Address already in use: 使用 `sudo fuser -k <port>/tcp`
3. Connection refused: 服务未启动，检查进程
