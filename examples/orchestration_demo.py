"""编排示例：视频制作任务"""

import sys
sys.path.insert(0, '/home/flybo/clawsjoy_v5')

from engine.orchestration.task_manager import task_manager

# 定义视频制作任务
video_tasks = [
    {
        "name": "collect_materials",
        "agent": "video_agent",
        "action": "search",
        "params": {"keyword": "AI 素材"},
        "depends_on": [],
        "rollback_action": "delete_temp_files",
        "checkpoint": True
    },
    {
        "name": "generate_script",
        "agent": "writer_agent",
        "action": "write",
        "params": {"topic": "AI发展趋势"},
        "depends_on": ["collect_materials"],
        "rollback_action": None,
        "checkpoint": True
    },
    {
        "name": "create_voice",
        "agent": "audio_agent",
        "action": "tts",
        "params": {"text": "脚本内容"},
        "depends_on": ["generate_script"],
        "rollback_action": "delete_audio",
        "checkpoint": False
    },
    {
        "name": "edit_video",
        "agent": "video_agent",
        "action": "edit",
        "params": {"duration": 60},
        "depends_on": ["collect_materials", "create_voice"],
        "rollback_action": "delete_video",
        "checkpoint": True
    },
    {
        "name": "add_subtitle",
        "agent": "video_agent",
        "action": "subtitle",
        "params": {},
        "depends_on": ["edit_video"],
        "rollback_action": None,
        "checkpoint": False
    }
]

# 创建计划
plan = task_manager.create_plan(
    name="AI视频制作",
    description="制作一个关于AI发展趋势的短视频",
    tasks=video_tasks
)

print(f"📋 创建计划: {plan.id}")
print(f"   任务数: {len(plan.tasks)}")
print(f"   状态: {plan.status.value}")

print("\n任务依赖关系:")
for task in plan.tasks:
    deps = ", ".join(task.depends_on) if task.depends_on else "无"
    print(f"  {task.name} → 依赖: {deps}")
