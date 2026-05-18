# 技能注册标准 v1.0

## 注册要求

每个技能必须满足以下条件才能被注册：

### 1. 清单文件 (manifest.json)
```json
{
  "name": "skill_name",
  "type": "atomic",
  "version": "1.0.0",
  "description": "清晰描述技能功能",
  "category": "分类",
  "author": "ClawsJoy",
  "input_schema": {
    "参数名": {"type": "类型", "required": true, "description": "说明"}
  },
  "output_schema": {
    "success": {"type": "boolean"},
    "result": {"type": "any"}
  },
  "test_cases": [
    {"input": {"param": "value"}, "expected": {"success": true}}
  ]
}
###2. 实现文件 (skill.py)
python
class SkillName:
    name = "skill_name"
    description = "功能描述"
    version = "1.0.0"
    category = "分类"
    
    def execute(self, params):
        # 实现
        return {"success": True, "result": value}

skill = SkillName()
###3. 测试通过
至少 1 个正向测试用例

所有测试必须通过
