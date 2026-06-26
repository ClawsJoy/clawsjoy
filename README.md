# ClawsJoy v6.0 - 通用 AI 智能体操作系统

## 定位
本地化部署的通用 AI 智能体操作系统。用户可二次开发垂直场景，通过 Skill 市场扩展能力。

## 核心能力

### 🧠 智能体引擎
- **意图识别**：fastText + 正则双引擎，口语化准确率 12/12
- **记忆管理**：MemoryBank 双引用，多租户隔离
- **22 个 Agent**：对话/代码/写作/翻译/计算/导演/记忆/文件/视频/音频/3D/方言...

### 📦 Skill 生态
- **28 个内置 Skill**：漫剧合成/TTS配音/字幕/图像分析/天气/网络...
- **社区市场**：双向兼容 OpenClaw，一键安装/发布
- **安全校验**：安装自动安全检查

### 🎬 垂直场景示例：漫剧工厂
- 小说创作 → 分镜剧本 → 角色资产 → 场景图 → 合成 → TTS 配音 → 字幕 → 视频

## 硬件要求
- Python 3.10+
- Ollama（qwen2.5:7b / llava）
- 6GB+ 显存（GPU）或 CPU 模式
- Linux / WSL / macOS

## 快速开始
```bash
git clone https://github.com/ClawsJoy/clawsjoy.git
cd clawsjoy
pip install -r requirements.txt
python agent_gateway_enhanced.py
访问 http://127.0.0.1:5002

二次开发
安装社区 Skill → web/skill_market.html

开发新 Agent → 继承 BusinessAgent

发布到社区 → developer_api.py

版本历史
v6.0：通用智能体操作系统，Skill 市场，漫剧工厂

v5.4：智慧化升级，联邦学习，多 Agent

v5.3：多轮对话，意图识别，代码生成
