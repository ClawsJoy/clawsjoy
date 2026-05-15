# Python 导入规则

## 项目内导入
- `from agents.xxx import` - 从 agents 目录导入
- `from bin.xxx import` - 从 bin 目录导入

## 常见错误
- ModuleNotFoundError: 模块路径不正确
- 解决方法: 添加 `sys.path.insert(0, '/mnt/d/clawsjoy')`
