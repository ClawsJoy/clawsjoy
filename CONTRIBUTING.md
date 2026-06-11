# 贡献指南

感谢你对 ClawsJoy 项目的关注！

## 开发环境设置

```bash
# 克隆仓库
git clone <repository>
cd clawsjoy_v5

# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 启动服务
./start_clawsjoy.sh
#代码规范
#使用 Black 格式化代码

#使用 pylint 检查代码质量

#添加类型注解

#编写单元测试

#提交规范
#使用 Conventional Commits 格式：

#feat: 新功能

#fix: 修复

#docs: 文档

#style: 格式

#refactor: 重构

#test: 测试

#chore: 构建/工具

#测试
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_intent_router.py
#Pull Request 流程
#Fork 项目

#创建功能分支

#提交更改

#推送到分支

创建 Pull Request
