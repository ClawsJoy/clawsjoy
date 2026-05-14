"""自校准执行器 - 带错误自愈"""
import traceback
from skills.manju_maker import skill as manju
from skills.self_calibrator import skill as calibrator
from skills.self_debug import skill as debugger
from skills.self_healer import skill as healer
from lib.memory_simple import memory

class CalibratedExecutorSkill:
    name = "calibrated_executor"
    description = "自校准执行器（带错误自愈）"
    version = "1.0.0"
    category = "executor"

    def execute(self, params):
        topic = params.get("topic", "")
        target_duration = params.get("target_duration", 60)
        max_attempts = params.get("max_attempts", 3)
        
        print(f"🎯 目标: {topic}, 时长{target_duration}秒")
        
        # 查询历史校准
        calib = memory.recall(f"校准|{topic}", category="calibration_log")
        adjusted_length = None
        if calib:
            import re
            match = re.search(r'建议字数(\d+)', calib[-1])
            if match:
                adjusted_length = int(match.group(1))
                print(f"📚 使用历史校准: 目标字数{adjusted_length}")
        
        for attempt in range(max_attempts):
            print(f"\n🔄 第{attempt+1}次尝试")
            
            try:
                current_topic = topic
                if adjusted_length:
                    current_topic = f"{topic} (脚本长度控制在{adjusted_length}字左右)"
                
                result = manju.execute({"topic": current_topic})
                
                if result.get("success") is False:
                    # 执行失败，尝试自愈
                    print("   ⚠️ 执行失败，尝试自愈...")
                    heal_result = healer.execute({"error": result.get("error", "")})
                    if heal_result.get("fixed"):
                        print(f"   ✅ 自愈成功: {heal_result.get('action')}")
                        continue  # 重试
                    else:
                        print(f"   ❌ 自愈失败: {heal_result.get('message')}")
                        return {"success": False, "error": result.get("error")}
                
                actual_duration = result.get("duration", 0)
                script_length = result.get("script_length", 0)
                
                print(f"   实际: {actual_duration:.1f}秒, 脚本{script_length}字")
                
                # 自校准
                calib_result = calibrator.execute({
                    "target_duration": target_duration,
                    "actual_duration": actual_duration,
                    "script_length": script_length,
                    "topic": topic
                })
                
                if not calib_result.get("need_adjust"):
                    print(f"✅ 达标! 时长{actual_duration:.1f}秒")
                    return {"success": True, "video": result.get("video"), "duration": actual_duration, "attempts": attempt+1}
                
                adjusted_length = calib_result.get("adjusted_script_length")
                print(f"   📝 调整: 目标字数{adjusted_length}")
                
            except Exception as e:
                error_msg = str(e)
                print(f"   ❌ 异常: {error_msg[:100]}")
                
                # 尝试自愈
                heal_result = healer.execute({"error": error_msg})
                if heal_result.get("fixed"):
                    print(f"   ✅ 自愈成功: {heal_result.get('action')}")
                    continue
                
                # 记录错误
                debug_result = debugger.execute({"error": error_msg})
                memory.remember(f"执行错误|{topic}|{error_msg[:100]}", category="execution_errors")
                return {"success": False, "error": error_msg}
        
        return {"success": False, "message": "多次尝试未达标"}

skill = CalibratedExecutorSkill()
