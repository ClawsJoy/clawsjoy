# ClawsJoy 版本管理规范

## 1. 版本体系

### 系统架构版本
- **格式**: `主.次.修订` (如 3.0.0)
- **文件**: `VERSION`
- **变更规则**:
  - 主版本: 重大架构重构，不向后兼容
  - 次版本: 功能增强，向后兼容
  - 修订号: Bug修复，完全兼容

### 模块独立版本
- **格式**: `v主.次.修订_YYYYMMDD` (如 v1.0.01_20260517)
- **存储**: `config/version_registry.json` + `.yaml`
- **来源**: 从文件名自动提取或 Git 生成

---

## 2. 文件版本命名规范

### Python 模块
格式: <模块名>v<主>.<次>.<修订><YYYYMMDD>.py

示例:
success_monitor_v1.0.01_20260517.py
task_queue_v3.0.01_20260520.py
version_registry_v1.0.03_20260517.py

### 配置文件
格式: <配置名>v<主>.<次>.<修订><YYYYMMDD>.yaml

示例:
monitoring_v1.0.01_20260517.yaml
agents_v3.0.00_20260517.yaml

---

## 3. 版本号递进规则

| 变更类型 | 版本号变化 | 示例 |
|----------|-----------|------|
| Bug修复 | 修订号 +1 | v1.0.01 → v1.0.02 |
| 功能增强 | 次版本 +1，修订号归零 | v1.0.05 → v1.1.00 |
| 重大重构 | 主版本 +1，其他归零 | v1.2.00 → v2.0.00 |

---

## 4. 目录结构
clawsjoy_clean/
├── VERSION # 系统版本 (3.0.0)
├── VERSION_SPEC.md # 本规范文档
│
├── .version_backup/ # 版本基线存储
│ ├── v3.0.00_20260517/ # 基线版本
│ │ ├── active_runner_v3.0.00_20260517.py
│ │ ├── task_queue_v3.0.00_20260517.py
│ │ ├── web_dashboard_v3.0.00_20260517.py
│ │ └── MANIFEST.txt
│ └── v3.0.01_20260517/ # 下一版本（待实现）
│
├── config/version/ # 配置版本
│ ├── v1.0.01_20260517/ # 配置版本目录
│ │ └── monitoring_v1.0.01.yaml
│ └── current -> v1.0.01_20260517
│
├── config/version_registry.json # 模块版本注册表（自动）
├── config/version_registry.yaml # 模块版本注册表（可读导出）
│
├── lib/version_registry.py # 统一导入入口
└── lib/version_registry_v*.py # 版本化实现

---

## 5. 修改流程

### 修改现有模块

```bash
# 1. 检查当前版本
python3 lib/version_registry.py list

# 2. 修改文件
vim lib/task_queue.py

# 3. 提交到 Git
git add lib/task_queue.py
git commit -m "fix: 修复任务队列bug"

# 4. 同步版本（自动更新修订号）
python3 lib/version_registry.py sync

# 5. 验证
python3 lib/version_registry.py list
创建新模块
# 1. 使用版本化文件名创建
cp lib/template.py lib/my_module_v1.0.00_20260517.py

# 2. 注册到版本中心
python3 lib/version_registry.py register "my_module" "lib/my_module_v1.0.00_20260517.py" "core"

# 3. 创建软链接（可选）
ln -sf lib/my_module_v1.0.00_20260517.py lib/my_module.py

6. 版本查询命令
# 查看系统版本
cat VERSION

# 查看所有已注册模块版本
python3 lib/version_registry.py list

# 查看注册中心状态
python3 lib/version_registry.py status

# 查看特定模块版本
python3 -c "
from lib.version_registry import version_registry
print(version_registry.get_version('success_monitor'))
"

# 在代码中获取版本
from lib.version_registry import version_registry
version = version_registry.get_version('task_queue')
7. 版本追溯
# 查看基线版本
ls .version_backup/

# 恢复到基线版本
cp .version_backup/v3.0.00_20260517/task_queue_v3.0.00_20260517.py lib/

# 查看版本历史
git log --oneline -- lib/task_queue.py

# 对比两个版本差异
diff .version_backup/v3.0.00_20260517/task_queue_v3.0.00_20260517.py \
     lib/task_queue.py
8. 角色与职责
角色	职责
架构师	维护 VERSION，审批主版本变更
开发者	遵循命名规范，提交后 sync
CI/CD	自动检测版本变化，触发测试
9. 规范检查清单
文件命名包含版本号和日期

修改后执行 version_registry.py sync

Git commit 信息关联版本号

重大变更更新 CHANGELOG

基线版本备份到 .version_backup/

10. 联系方式
规范维护: 架构组

最后更新: 2026-05-17

版本: 1.0.0
