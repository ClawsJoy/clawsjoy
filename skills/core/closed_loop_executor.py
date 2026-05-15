"""闭环执行器 - 执行 → 检查 → 优化 → 重试"""
from skills.task_optimizer import skill as optimizer
from skills.manju_maker import skill as manju_maker
from skills.release_decision import skill as release
from lib.memory_simple import memory

class ClosedLoopExecutorSkill:
    name = "closed_loop_executor"
    description = "闭环执行：生成→检查→优化→重试"
    version = "1.0.0"
    category = "executor"

    def execute(self, params):
        task = params.get("task", "")
        max_attempts = params.get("max_attempts", 3)
        
        # 1. 生成初始标准
        print(f"🎯 任务: {task}")
        standard = optimizer.execute({"task": task})
        print(f"📊 目标标准: 时长{standard['target']['duration']}秒, 字数{standard['target']['script_length']}")
        
        for attempt in range(max_attempts):
            print(f"\n🔄 第 {attempt + 1} 次尝试")
            
            # 2. 执行任务
            result = manju_maker.execute({
                "topic": task,
                "target_duration": standard['target']['duration']
            })
            
            # 3. 质量检查
            quality = release.execute({
                "video_path": result.get("video", ""),
                "script": result.get("script", ""),
                "keywords": standard.get("key_points", [])
            })
            
            print(f"   得分: {quality['score']}, 决策: {quality['decision']}")
            
            # 4. 达标则返回
            if quality["can_publish"]:
                print(f"✅ 第{attempt + 1}次尝试达标!")
                memory.remember(f"任务成功|{task}|尝试次数:{attempt + 1}", category="task_success")
                return {"success": True, "result": result, "quality": quality, "attempts": attempt + 1}
            
            # 5. 未达标，分析改进
            issues = [k for k, v in quality['checks'].items() if not v]
            analysis = optimizer.execute({
                "task": task,
                "previous_result": {
                    "duration": result.get("duration", 0),
                    "script_length": len(result.get("script", "")),
                    "issues": issues
                }
            })
            
            print(f"   📝 改进方案: {analysis.get('improvements', [])}")
            
            # 6. 更新标准用于下次尝试
            standard['target'] = analysis.get('target', standard['target'])
        
        print(f"❌ {max_attempts}次尝试后仍未达标")
        memory.remember(f"任务失败|{task}|尝试次数:{max_attempts}", category="task_failure")
        return {"success": False, "attempts": max_attempts, "last_quality": quality}

skill = ClosedLoopExecutorSkill()
