# ClawsJoy 修复固化版本

## 修复日期
2026-05-26

## 修复内容

### 1. 配置系统
- unified_config 统一配置入口
- 配置热重载支持

### 2. 向量记忆
- vector_memory_simple 简化版
- 租户向量索引

### 3. 私人管家
- 向量记忆召回
- MemoryAgent 集成
- 配置驱动

### 4. 技能市场
- 技能推荐向量索引
- 安全扫描

### 5. 路由系统
- routes.yaml 完善
- 权限分级

### 6. 用户数据
- 用户数据资产管理
- 申请审核流程

### 7. 云端算力
- Diffusion Studio 集成
- ComfyUI 双模式

## 固化文件清单
- core/lib/unified_config.py
- core/tenant/hot_reload_manager.py
- core/agents/personal_butler_v2.py
- api/skill_market.py
- config/routes.yaml
- lib/memory.py
- lib/user_data_manager.py
- lib/cloud/diffusion_studio.py
