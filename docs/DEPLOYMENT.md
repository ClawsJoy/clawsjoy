# ClawsJoy 部署指南

## 系统要求

- Python 3.11+
- 8GB+ RAM（推荐 16GB）
- 10GB+ 磁盘空间
- Linux / WSL2 / macOS

## 快速部署

### 方式一：本地部署（推荐开发）

```bash
# 1. 克隆项目
git clone https://github.com/your-repo/clawsjoy.git
cd clawsjoy

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境
cp .env.example .env
# 编辑 .env 文件

# 4. 启动服务
./start_all.sh
### 方式二：Docker 部署（推荐生产）
# 1. 构建并启动
./start_docker.sh up

# 2. 查看日志
./start_docker.sh logs

# 3. 停止服务
./start_docker.sh down
### 方式三：systemd 服务（开机自启）
# 1. 创建用户服务
mkdir -p ~/.config/systemd/user
cp clawsjoy.service ~/.config/systemd/user/

# 2. 启动服务
systemctl --user daemon-reload
systemctl --user enable clawsjoy
systemctl --user start clawsjoy

# 3. 查看状态
systemctl --user status clawsjoy

#配置说明
环境变量 (.env)

# 服务端口
CLAWSJOY_GATEWAY_PORT=5002
CLAWSJOY_FILE_PORT=5003
CLAWSJOY_MULTI_PORT=5005
CLAWSJOY_DOC_PORT=5008
CLAWSJOY_AGENT_API_PORT=5010
CLAWSJOY_WEB_PORT=5011

# LLM 配置
OLLAMA_HOST=http://127.0.0.1:11434
CLAWSJOY_DEFAULT_MODEL=qwen2.5:7b
CLAWSJOY_FAST_MODEL=qwen2.5:3b

# 调试模式
DEBUG=false
LOG_LEVEL=INFO

#验证部署
# 健康检查
curl http://localhost:5002/api/health

# 查看服务状态
./stop_all.sh && ./start_all.sh
#故障排查
问题	解决方案
端口被占用	lsof -i:5002 查看占用进程
Ollama 连接失败	确认 ollama serve 正在运行
技能加载失败	检查 skills/ 目录权限
