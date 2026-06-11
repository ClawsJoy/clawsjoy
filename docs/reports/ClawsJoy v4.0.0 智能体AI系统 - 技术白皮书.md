# ClawsJoy v4.0.0 智能体AI系统 - 技术白皮书

**版本**: 4.0.0  
**发布日期**: 2026-05-20  
**受众**: 行业同行、技术决策者、架构师


## 一、项目概述

ClawsJoy 是一个**配置驱动的智能体AI系统**，核心特点是**用户数据本地化**和**钩子驱动架构**。与市面上依赖云端的 AI 助手不同，ClawsJoy 将用户隐私作为首要设计原则。

### 1.1 核心差异化优势

| 特        性 | ClawsJoy | 市面竞品 |
|-----       -|--------  --|----------|
| 数据存储 | 本地加密存储 | 云端存储 |
| 用户隐私 | 端到端加密，用户唯一密钥 | 平台掌握数据 |
| 记忆能力 | L0-L4 多层记忆，持久化 | 无状态或短期记忆 |
| 扩 展 性   | 配置驱动，无需编码 | 需要 API 开发 |
| 部署方式 | 本地优先，可私有化部署 | 纯 SaaS |
| 成       本 | 本地运行，无订阅费 | 按量/订阅收费 |

### 1.2 技术架构图
┌─────────────────────────────────────────────────────────────────┐
│ 用户层 │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │ 游客 │ │ 注册用户 │ │ 开发者 │ │
│ │ 品牌浏览 │ │ 私人管家 │ │ 技能上架 │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│ 客户端层 │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Electron 桌面客户端 + Web 界面 │ │
│ │ - 本地加密存储 (AES-256-GCM) │ │
│ │ - 插件系统 (动态驱动加载) │ │
│ │ - 敏感信息脱敏 │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│ API 网关层 │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Flask + 配置驱动路由 + 钩子系统 │ │
│ │ - YAML 配置驱动，无需编码 │ │
│ │ - 20+ API 端点 │ │
│ │ - 热重载支持 │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│ Agent 层 │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 10 个专业 Agent + 116 个技能 │ │
│ │ - 任务编排器 (orchestrator) │ │
│ │ - 私人管家 (personal_butler) - 用户数字分身 │ │
│ │ - 代码助手 (code_agent) │ │
│ │ - 视频制作 (video_agent) │ │
│ │ - 安全助手 (security_agent) │ │
│ │ - 记忆管理 (memory_manager) │ │
│ │ - 数据分析 (analysis_agent) │ │
│ │ - 决策引擎 (decision_agent) │ │
│ │ - YouTube 助手 (youtube_agent) │ │
│ │ - 聊天助手 (chat_agent) │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│ 数据层 │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 向量记忆库 (ChromaDB) - 1062 条 │ │
│ │ 知识库 - 53 条 │ │
│ │ 用户数据 - 本地加密存储 │ │
│ │ 技能库 - 116 个 │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│ 闭环系统 │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 采集 → 分析 → 建议 → 执行 → 反馈 → 学习 │ │
│ │ (6/6 阶段完整) │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘

---

## 二、核心模块详解

### 2.1 配置驱动路由系统

**设计理念**: 所有路由通过 YAML 配置，无需修改代码即可增删改 API。

**配置文件**: `config/routes.yaml`

```yaml
routes:
  - path: "/api/health"
    method: "GET"
    handler: "health"
    enabled: true
    description: "健康检查"

已注册路由: 20 条

分类 	     路由数	说明
Web 前端	2	主页 + 静态文件
系统管理	        2	健康检查 + 管理员接口
技能系统	        3	列表/执行/大脑任务
Agent 管理	7	列表/健康/消息/广播/订阅
日志系统        	3	获取/搜索/错误
其他         	3	服务列表/监控指标/聊天

2.2 钩子系统

设计理念: 可插拔的安全、学习、备份机制，配置驱动，消除硬编码。

配置文件: config/hooks.yaml
data:
  before_save:
    - name: "encrypt_sensitive"
      module: "lib.security_hooks"
      function: "encrypt_sensitive"
      enabled: true

已注册钩子: 11 个

钩子点	                                功能	                        状态
data:before_save	                保存前加密 + 脱敏	✅
data:after_load	                加载后解密 + 验证	✅
request:before_process	请求预处理	        ✅
request:after_process	        响应后记录 + 学习	✅
security:before_encrypt	加密前准备	        ✅
security:after_decrypt	        解密后清理	        ✅

2.3 安全体系

设计理念: 用户数据永不离开用户设备，端到端加密。
用户输入 → 本地脱敏 → 本地加密 → 发送密文到服务器
                                    ↓
                              服务器处理密文
                                    ↓
                              返回密文结果
                                    ↓
用户接收 → 本地解密 → 最终输出
加密算法: AES-256-GCM
脱敏规则:

手机号: 138****1234

身份证: 1101**********1234

邮箱: ab***@example.com

API Key: sk-***[API_KEY]

2.4 Agent 系统
10 个专业 Agent:

Agent	                类型	                   能力
orchestrator	        核心	                   任务编排、技能调度
personal_butler	核心	                   用户数字分身、偏好记忆
chat_agent	        核心	                   游客对话、临时会话
decision_agent	核心	                   任务调度、决策
security_agent	核心         	   权限验证、安全检查
memory_manager	核心	                   记忆存储、检索
analysis_agent	核心	                   数据分析、优化建议
code_agent	        专业	                   代码生成、审查、调试
video_agent	        专业	                   视频制作、字幕添加
youtube_agent	专业	                   视频上传、频道分析

2.5 技能系统
116 个技能，分为 12 个分类:

分类	数量	示例
核心调度	14	workflow_engine, orchestrator
数学计算	8	add, multiply, sqrt, mod
图像处理	5	remove_bg, ai_image, image_slideshow
视频制作	7	manju_maker, video_composer, ffmpeg_video
文本处理	9	to_upper, reverse, trim
音频处理	2	tts, whisper_transcribe
网络服务	6	http_get, download_file, youtube_uploader
记忆系统	10	memory_query, memory_enhanced
自愈系统	11	self_heal, error_analyzer
工具集	23	file_processor, regex, json_parser
包装器	17	intent_parser, state_manager
自动生成	6	skill_generator, self_designer

2.6 知识库系统
双知识库架构:

知识库	               用途	                        当前容量
向量记忆库	语义搜索、经验存储	1062 条
Agents知识库	报告/技能/Agent 文档	53 条
Agents 知识库组成:

reports: 5 条 (开发者/用户/投资人/管理员报告)

skills: 34 条 (技能文档)

agents_doc: 10 条 (Agent 文档)

learning_patterns: 4 条 (学习模式)

2.7 闭环系统

完整 6 阶段闭环:
采集 → 分析 → 建议 → 执行 → 反馈 → 学习
 ✅     ✅     ✅     ✅     ✅     ✅

阶段	                  实现模块	                                        状态
数据采集	          collector_agent, metrics_collector	✅
数据分析	          analysis_agent, unified_analyzer	✅
生成建议	          suggestion_engine	                        ✅
任务执行	          Agent 系统 + 技能系统	                        ✅
结果反馈	          feedback_handler	                        ✅
自我学习	          learning_hooks, fault_learning_loop	✅

三、客户端

3.1 Electron 桌面客户端
支持平台: Windows / Linux

核心功能:

本地加密存储 (AES-256-GCM)

插件系统 (动态驱动加载)

敏感信息自动脱敏

与后端安全通信

安装包大小: 72.7 MB (Windows)

3.2 插件系统

设计理念: 服务器下发驱动，客户端本地执行，数据不离开用户设备。
// 插件 API 示例
await ipcRenderer.invoke('plugin:save-data', { key, data });
await ipcRenderer.invoke('plugin:load-data', key);
await ipcRenderer.invoke('plugin:select-file');
四、部署与运维
4.1 部署要求
组件	要求
Python	              3.13+
Node.js	              18+ (客户端)
内存	                      最低 4GB，推荐 8GB+
磁盘	                      最低 10GB，推荐 20GB+
LLM (可选)	      Ollama + Qwen2.5
4.2 启动命令
# 启动后端
cd ~/clawsjoy_clean
python agent_gateway_web.py

# 启动客户端
cd client
npm start

# 打包 Windows 安装包
npm run build:win
4.3 监控指标
指标	当前值
Agent 数量	10
技能数量         	116
API 端点  	20
钩子数量  	11
向量记忆  	1062 条
日志大小  	11.1 MB
磁盘占用  	< 5GB

五、技术债务清理

原问题	          解决方案	                状态
硬编码路由	  配置驱动 routes.yaml	✅
硬编码钩子	  配置驱动 hooks.yaml	✅
明文存储          AES-256-GCM 加密	✅
敏感信息泄露	自动脱敏                  	✅
无学习机制	学习钩子 + 闭环系统	✅
无备份	        自动备份钩子	                ✅
硬编码提示词	提示词配置文件        	✅
硬编码超时	统一超时配置	                ✅
硬编码密码	环境变量                  	✅

六、项目统计

项目	                  数据
代码行数	         ~50,000
配置文件	         7 个
Python 模块   	200+
技能数量  	116
Agent 数量	10
API 端点  	20
钩子数量	        11
向量记忆	        1062 条
客户端大小	72.7 MB

七、技术选型

层级	技术	版本
后端框架	                 Flask	                        3.1.x
Agent 框架	         自研	                        4.0.0
LLM 集成	                 Ollama + Qwen2.5	7b/3b
向量数据库	         ChromaDB	                1.5.9
加密算法	                 AES-256-GCM	         -
桌面客户端	         Electron	                         28.x
前端	                         HTML/CSS/JS         	 -
配置管理	                 YAML                      	 -

八、竞品对比总结

维度  	        ClawsJoy	         竞品
数据主权  	✅ 用户完全掌控	❌ 平台掌控
隐私保护	        ✅ 端到端加密	⚠️ 传输加密
记忆能力	        ✅ L0-L4 多层记忆	⚠️ 短期记忆
扩展性	        ✅ 配置驱动	        ⚠️ 需 API 开发
部署灵活性	✅ 本地/SaaS 皆可	❌ 仅 SaaS
成本	                ✅ 无订阅费	        ❌ 按量/订阅
开箱技能	        ✅ 116 个	        ⚠️ 有限

九、联系方式

项目地址: ~/clawsjoy_clean

技术文档: docs/reports/

版本: 4.0.0

发布日期: 2026-05-20

ClawsJoy - 让智能体真正属于用户
本回答由 AI 生成，内容仅供参考，请仔细甄别。