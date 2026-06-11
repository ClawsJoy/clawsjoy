#部署指南
#开发环境部署
#1. 安装依赖
#pip install -r requirements.txt
#2. 启动 Ollama
#ollama serve
#ollama pull qwen2.5:3b
#3. 启动服务
#./start_clawsjoy.sh
#4. 验证
#curl http://localhost:5002/health
#生产环境部署
#使用 systemd
#创建服务文件 /etc/systemd/system/clawsjoy.service:
[Unit]
Description=ClawsJoy AI Assistant
After=network.target

[Service]
Type=simple
User=flybo
WorkingDirectory=/home/flybo/clawsjoy_v5
ExecStart=/home/flybo/clawsjoy_v5/start_clawsjoy.sh
Restart=always

[Install]
WantedBy=multi-user.target
#使用 Docker (推荐)
FROM python:3.10-slim

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

EXPOSE 5002
CMD ["./start_clawsjoy.sh"]
#环境变量
JWT_SECRET=your-secret-key
JWT_EXPIRE_HOURS=24
LOG_LEVEL=INFO
#监控
#健康检查: http://localhost:5002/health

#日志位置: logs/gateway.log

#备份
# 备份记忆数据
tar -czf backup_$(date +%Y%m%d).tar.gz data/memories/
