# ClawsJoy 前端开发备忘录

## 一、项目信息

| 项目 | 内容 |
|------|------|
| 项目名称 | ClawsJoy 智能体AI系统 |
| 客户端类型 | Windows 桌面客户端 (Electron) |
| 后端地址 | WSL: http://localhost:5002 |
| 设计风格 | 科幻极简未来风、树形层级架构 |
| 当前版本 | v4.0.0 |
| 最后更新 | 2026-05-20 |

## 二、用户权限分层

| 用户类型 | 可见模块 | 操作权限 |
|---------|---------|---------|
| 游客 | 品牌形象区、商务展示区 | 仅浏览 |
| 投资人 | 品牌形象区、商务展示区（含商业数据） | 浏览 + 商务咨询 |
| 注册用户 | 全部普通功能 | 使用 + 购买技能 |
| 开发者 | 全部功能 + 开发者工作区 | 开发 + 上架技能 |
| 企业用户 | 全部功能 + 数字员工 + 多智能体 | 训练 + 部署 |

## 三、树形菜单结构
ClawsJoy
├── 🌟 品牌形象 (游客/投资人)
├── 💼 商务展示 (游客/投资人)
├── 👤 个人中心 (登录后)
├── 💬 私人管家 (登录后)
├── 🔧 AI工具集 (登录后)
├── 🏪 生态社区 (登录后)
├── 🛠️ 开发者工作区 (开发者)
├── 📊 监控中心 (登录后)
└── ⚙️ 设置 (登录后)

## 四、科幻视觉规范

```css
/* 核心变量 */
--space-bg: #0a0a1a;      /* 深空背景 */
--neon-cyan: #00f3ff;      /* 流光青 */
--neon-purple: #b000ff;    /* 流光紫 */
--glow-cyan: 0 0 10px rgba(0,243,255,0.5);
--border-cyber: 1px solid rgba(0,243,255,0.3);
五、技术栈
层级	技术
桌面框架	Electron 28+
前端框架	Vue 3 / React 18
UI组件	自研 + TailwindCSS
状态管理	Pinia / Zustand
HTTP客户端	Axios
工作流编排	React Flow
代码编辑	Monaco Editor
视频处理	FFmpeg.wasm
六、开发阶段
阶段	内容	工时
P0	框架 + 登录认证	2天
P1	品牌形象 + 商务展示	2天
P2	私人管家 + AI工具	3天
P3	生态社区 + 技能商店	3天
P4	开发者工作区	5天
P5	视频工具	3天
P6	监控中心 + 设置	2天
P7	打包发布	2天
七、后端API清单
API	用途	方法
/api/auth/login	登录	POST
/api/auth/register	注册	POST
/api/user/profile	用户信息	GET
/api/skills/store/list	技能商店	GET
/api/skills/install	安装技能	POST
/api/skills/publish	发布技能	POST
/api/workflow/save	保存工作流	POST
/api/employees/*	数字员工	各种
八、当前进度
✅ 后端服务运行中 (WSL)

✅ Windows 客户端基础框架

✅ 登录认证对接

✅ 私人管家对话功能

🔄 开发者工作区开发中

⏳ 技能商店开发中

⏳ 视频工具开发中

九、待解决问题
语音交互连续对话

技能商店后端API对接

工作流可视化编排

视频工具本地渲染

数字员工训练流程

打包exe安装程序

十、参考资料
项目路径: C:\clawsjoy_client

WSL服务: ~/clawsjoy_clean

启动命令: npm start

打包命令: npm run build