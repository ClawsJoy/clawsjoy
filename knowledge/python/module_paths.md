# Python 模块导入

## 项目结构
/mnt/d/clawsjoy/
├── agents/      # Agent 模块
├── bin/         # 可执行脚本
├── web/         # 前端
└── data/        # 数据

## 导入规则
1. 项目内导入: from agents.xxx import
2. 正确路径: sys.path.insert(0, '/mnt/d/clawsjoy')
3. 常见错误: ModuleNotFoundError → 检查导入路径

## 修复方法
# 在脚本开头添加
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')
