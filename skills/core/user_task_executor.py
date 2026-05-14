"""用户任务执行器 - 从意图到完成"""
from skills.intent_parser import skill as parser
from skills.manju_maker import skill as manju_maker
from lib.memory_simple import memory

class UserTaskExecutorSkill:
    name = "user_task_executor"
    description = "执行用户任务：意图→标准→执行→评估"
    version = "1.0.0"
    category = "executor"

    def execute(self, params):
        user_input = params.get("input", "")
        
        print(f"📝 用户诉求: {user_input}")
        
        # 1. 解析意图，生成任务标准
        task_spec = parser.execute({"input": user_input})
        
        if "error" in task_spec:
            return {"error": task_spec["error"]}
        
        print(f"🎯 解析结果:")
        print(f"   主题: {task_spec.get('topic', '未知')}")
        print(f"   目标时长: {task_spec['target'].get('duration', 60)}秒")
        print(f"   目标字数: {task_spec['target'].get('script_length', 180)}字")
        print(f"   合格阈值: {task_spec.get('quality_threshold', 60)}分")
        
        # 2. 执行任务
        print(f"\n🎬 开始制作...")
        result = manju_maker.execute({
            "topic": task_spec.get("topic", user_input),
            "target_duration": task_spec['target'].get('duration', 60)
        })
        
        actual_duration = result.get("duration", 0)
        script_len = result.get("script_length", 0)
        
        # 3. 评分
        target_duration = task_spec['target'].get('duration', 60)
        target_script = task_spec['target'].get('script_length', 180)
        
        duration_score = min(100, int(actual_duration / target_duration * 100)) if target_duration else 50
        script_score = min(100, int(script_len / target_script * 100)) if target_script else 50
        total_score = (duration_score + script_score) // 2
        
        is_pass = total_score >= task_spec.get('quality_threshold', 60)
        
        print(f"\n📊 执行结果:")
        print(f"   实际时长: {actual_duration:.1f}s (目标{target_duration}s) 得分:{duration_score}")
        print(f"   实际字数: {script_len}字 (目标{target_script}字) 得分:{script_score}")
        print(f"   综合得分: {total_score} {'✅ 达标' if is_pass else '❌ 未达标'}")
        
        # 4. 记录成功经验
        if is_pass:
            memory.remember(
                f"任务成功|诉求:{user_input[:50]}|时长:{actual_duration}|脚本:{script_len}|得分:{total_score}",
                category="task_success_reference"
            )
        
        return {
            "success": is_pass,
            "task_spec": task_spec,
            "result": result,
            "score": total_score,
            "video": result.get("video")
        }

skill = UserTaskExecutorSkill()
