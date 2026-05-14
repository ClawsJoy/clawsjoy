"""
技能基础模板 - 所有技能必须遵循此结构

每个技能文件必须包含:
1. 继承 BaseSkill
2. 定义 name, description, version, category
3. 实现 execute(params) -> Dict
4. 必须有 skill = YourSkill() 实例
"""

from typing import Dict, Any
from skills.skill_interface import BaseSkill

class YourSkill(BaseSkill):
    name = "skill_name"           # 唯一标识，小写+下划线
    description = "技能描述"       # 一句话说明功能
    version = "1.0.0"             # 语义化版本
    category = "content"          # content/video/publish/api/tool
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行技能
        
        输入参数规范:
        - 必须包含必要的参数验证
        - 使用 .get() 方法获取参数，提供默认值
        
        返回格式规范:
        - success: bool - 是否成功
        - 成功时返回具体数据
        - 失败时返回 error: str
        """
        # 1. 参数验证
        required = params.get("required_param")
        if not required:
            return {"success": False, "error": "required_param is required"}
        
        # 2. 执行业务逻辑
        # ...
        
        # 3. 返回结果
        return {
            "success": True,
            "data": "result"
        }

# 必须创建全局实例
skill = YourSkill()
