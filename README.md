# ClawsJoy v6.0 - 本地AI矩阵系统

## 简介
ClawsJoy 是一个本地 AI 矩阵系统，支持 22 个 Agent 协作、漫剧工厂、意图识别、记忆管理。

## v6.0.0 - 漫剧工厂 (当前版本)

### 🎬 漫剧生产流水线
- **小说创作**: WriterAgent 17章AI觉醒，支持session自动恢复
- **分镜剧本**: ComicWriterAgent 小说→分镜剧本
- **角色资产**: 林浩14张（三视图/表情/道具），豆包/即梦出图
- **场景图**: DreamShaper SDXL 出图
- **分镜合成**: rembg抠图+Pillow合成+亮度匹配
- **表情切换**: 对白关键词自动匹配角色表情
- **镜头运动**: zoompan规则引擎（推/拉/摇/静）
- **视频输出**: ffmpeg concat → MP4

### 🎯 DirectorAgent 导演闭环
- llava(CPU)逐帧审片 → qwen(GPU)评分+建议
- 综合评分(1-5)、缺失素材清单、改进建议
- video-description: 逐帧描述+分析日志

### 🧠 意图识别升级
- **fastText 分类器**: 口语化识别准确率 12/12
- 全局单例加载，<1ms 推理
- 正则降级为 fallback

### 🔧 核心修复
- Intent Router WRITE/READ 分流，写入不检索历史
- MemoryBank 双引用 permanent_memory，零双写
- 多租户隔离：agent_pool 按 user_id 区分
- cache_manager 缓存键含 user_id
- LLM 模型统一为 qwen2.5:7b-instruct-q4_0

### 📦 新增 Skill
- comic_compositor: 漫剧分镜合成
- expression-switcher: 对白→表情匹配
- video-description: 视频逐帧分析
- vision_log: 图片自动描述存档
- export_fasttext: 训练数据导出


## 版本历史

### v5.4.0 - 智慧化升级
- 8个智慧Agent: Chat/Code/Analysis/Butler/Translate/Calculator/Orchestrator/Decision
- 联邦学习: Agent间知识共享
- 科学计算器、多语言翻译、任务编排

### v5.3.0 - 基础版本
- 多轮对话记忆、持久化存储、意图识别、代码生成
