# 技能注册规范 v1.0

## 技能清单格式 (manifest.json)

```json
{
  "name": "script_generator",
  "type": "atomic",
  "version": "1.0.0",
  "description": "根据主题生成短视频脚本，用于 LLM 理解技能功能",
  "category": "text",
  "author": "ClawsJoy",
  "compatible_with": ["openclaw", "clawsjoy"],
  "tags": ["script", "generation", "llm"],
  "input_schema": {
    "topic": {"type": "string", "required": true, "description": "视频主题"},
    "duration": {"type": "integer", "required": false, "default": 30}
  },
  "output_schema": {
    "script": {"type": "string", "description": "生成的脚本"},
    "success": {"type": "boolean"}
  },
  "llm_prompt_template": "为「{topic}」生成{duration}秒短视频脚本",
  "examples": [{"input": {"topic": "上海"}, "output": {"script": "..."}}]
}
字段说明
字段	类型	必填	说明
name	string	✅	技能唯一标识
type	string	✅	atomic / workflow
description	string	✅	LLM 理解技能用途的关键
category	string	✅	text/audio/video/image/data/network/math
input_schema	object	✅	输入参数定义
output_schema	object	✅	输出格式定义
llm_prompt_template	string	❌	调用 LLM 时的提示词模板
