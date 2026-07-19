# ClawsJoy V9

**AI 劳动力管理平台 + Agent 工作区** — 一人公司老板聘 AI 员工，频道里派活。Agent 工作区提供代码修改、测试验证、异步执行、代码索引等开发能力。本地运行，开源免费。

## V9 系统工程化亮点

- **前置检测**：文件已完成时零 Token 直接返回
- **项目树注入**：Agent 启动前注入完整目录结构 + 元信息（行数/函数签名）
- **配额硬限制**：read_file 5/10次、list_dir 3次，超限拒绝
- **路径自动补全**：静默修正路径前缀，known_patterns 记录
- **大项目摘要**：>50 文件自动切换摘要模式，上下文压缩 98%

## 性能对比

| 指标 | V8 | V9 |
|------|:--:|:--:|
| 已知任务判定 | 20+ 轮读取 | 0 调用 |
| list_dir 探索 | 5-6 次 | 0 次 |
| 上下文大小 | 325K tokens | 76K tokens |

## 快速开始

```bash
git clone https://github.com/ClawsJoy/clawsjoy.git
cd clawsjoy
pip install -r requirements.txt
cp config/.env.example config/.env  # 填入 DeepSeek API Key
python3 agent_gateway_enhanced.py   # 启动 :5002
浏览器访问 http://localhost:5002/web/dashboard/workbench.html

架构
Flask Gateway (:5002)
    → Cortex (意图路由)
    → Agent 集群 (24+)
    → DeepSeek / GLM / Ollama
License
MIT
