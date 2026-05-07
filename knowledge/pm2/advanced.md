# PM2 进程管理

## 常用命令
- pm2 list                    # 查看所有进程
- pm2 logs <name> --lines 100 # 查看日志
- pm2 monit                   # 实时监控
- pm2 save                    # 保存当前配置
- pm2 startup                 # 开机自启

## 故障排查
pm2 describe <name>           # 查看进程详情
pm2 show <name>               # 查看详细信息
pm2 reset <name>              # 重置重启计数

## 配置文件 ecosystem.config.js
module.exports = {
  apps: [{
    name: 'chat-api',
    script: 'bin/chat_api.py',
    interpreter: 'python3',
    args: '--port 18109',
    autorestart: true,
    watch: false,
    max_memory_restart: '500M',
    error_file: 'logs/chat-api-error.log',
    out_file: 'logs/chat-api-out.log'
  }]
}
