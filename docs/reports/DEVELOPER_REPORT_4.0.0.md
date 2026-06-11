# ClawsJoy 开发者技术报告 v4.0.0

**版本**: 4.0.0  
**日期**: 2026-05-20  
**受众**: 开发者、系统架构师

---

## 一、系统架构

### 1.1 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| 后端框架 | Flask | 3.1.x |
| Agent框架 | 自研 | 4.0.0 |
| LLM集成 | Ollama + Qwen2.5 | 7b/3b |
| 桌面客户端 | Electron | 28.x |
| 加密算法 | AES-256-GCM | - |

### 1.2 核心模块

- **配置驱动路由** (`config/routes.yaml`)
- **钩子系统** (`config/hooks.yaml`, `lib/hook_manager.py`)
- **Agent管理器** (`config/agents.yaml`, `core/agents/`)
- **技能系统** (116个技能)
- **加密/脱敏** (`lib/security_hooks.py`)
- **学习系统** (`lib/learning_hooks.py`)
- **备份系统** (`lib/backup_hooks.py`)

---

## 二、API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 前端首页 |
| `/api/health` | GET | 健康检查 |
| `/api/chat` | POST | 聊天接口 |
| `/api/skills` | GET | 技能列表 |
| `/api/skills/execute` | POST | 执行技能 |
| `/api/agents/list` | GET | Agent列表 |

---

## 三、配置驱动示例

### routes.yaml
```yaml
routes:
  - path: "/"
    method: "GET"
    handler: "web_index"
    enabled: true
hooks.yaml
data:
  before_save:
    - name: "encrypt_sensitive"
      module: "lib.security_hooks"
      function: "encrypt_sensitive"

##四、部署命令

# 启动后端
cd ~/clawsjoy_clean
python agent_gateway_web.py

# 启动客户端
cd client
npm start

# 打包 Windows
npm run build:win
报告生成: 2026-05-20