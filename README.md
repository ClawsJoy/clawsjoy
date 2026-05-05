# ClawsJoy / JoyMate

AI 驱动的智能助手平台，支持 Docker 部署，集成 Ollama。

## 快速启动

\`\`\`bash
# 1. 复制环境变量
cp .env.example .env

# 2. 启动 Docker 后端
docker-compose up -d

# 3. 启动 Chat API
cd bin && nohup python3 chat_api_agent.py &

# 4. 启动前端（Windows）
start python -m http.server 8082 --directory web
\`\`\`

## 服务端口

| 服务 | 端口 |
|------|------|
| Web 前端 | 8082 |
| Tenant API | 8088 |
| Task API | 8084 |
| Chat API | 8101 |
| Ollama | 11434 |

## 技术栈

- Python 3.10+
- Docker + Docker Compose
- Ollama (qwen:0.5b)
- PM2 进程管理
- SQLite

## 安全注意事项

- 所有密钥使用环境变量
- 数据库文件已加入 .gitignore
- 生产环境请更换 SECRET_KEY
