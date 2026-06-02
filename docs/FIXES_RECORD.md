# ClawsJoy 修复记录

## 2026-05-26 会话修复

### 1. 后端修复

#### 1.1 向量记忆
- 文件: `core/old/vector_memory_simple.py`
- 修复: 移除 config_helper 依赖，使用 unified_config

#### 1.2 私人管家
- 文件: `core/agents/personal_butler_v2.py`
- 修复: 
  - 添加向量记忆召回
  - 修复 config_helper 引用
  - 集成 MemoryAgent

#### 1.3 技能推荐
- 文件: `api/skill_market.py`
- 修复: skill_recommender 使用 skill_loader 索引 139 个技能

#### 1.4 路由系统
- 文件: `config/routes.yaml`
- 修复: 添加缺失路由（butler_chat, recommend_skills, etc.）

#### 1.5 统一配置
- 文件: `core/lib/unified_config.py`
- 修复: 移除循环导入

### 2. 客户端修复

#### 2.1 API 路径
- 文件: `C:\clawsjoy_client\renderer\core\butler.html`
- 修复: `/api/chat` → `/api/butler/chat`

#### 2.2 API_URL
- 文件: 同上
- 修复: `const API_URL = "http://localhost:5002";`

#### 2.3 管家名称持久化
- 文件: 同上
- 修复: localStorage 保存管家名称

### 3. 新增模块

#### 3.1 用户数据管理
- 文件: `lib/user_data_manager.py`

#### 3.2 云端算力
- 文件: `lib/cloud/diffusion_studio.py`

#### 3.3 权限装饰器
- 文件: `lib/permission_decorator.py`

### 4. 配置文件

#### 4.1 路由配置
- `config/routes.yaml` - 36+ 路由

#### 4.2 权限配置
- `config/permissions.yaml`

#### 4.3 云端配置
- `config/cloud_services.yaml`
- `config/diffusion_studio.yaml`

