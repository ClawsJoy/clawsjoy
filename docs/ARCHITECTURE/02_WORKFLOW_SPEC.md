
工作流定义规范 v1.0
工作流清单格式
{
  "name": "video_creation",
  "type": "workflow",
  "version": "1.0.0",
  "description": "完整的视频制作流程：脚本生成 → 音频生成 → 视频合成",
  "steps": [
    {
      "skill": "script_generator",
      "params": {"topic": "{input.topic}"},
      "output": "script",
      "on_error": "abort"
    },
    {
      "skill": "audio_generator", 
      "params": {"text": "{steps.script.output.script}"},
      "output": "audio",
      "on_error": "retry"
    },
    {
      "skill": "video_composer",
      "params": {"audio_path": "{steps.audio.output.audio_path}"},
      "output": "video",
      "on_error": "abort"
    }
  ],
  "dependencies": ["script_generator", "audio_generator", "video_composer"]
}
步骤字段说明
字段	说明
skill	调用的原子技能名称
params	参数，支持变量引用
output	输出变量名
on_error	错误处理：abort/retry/skip
