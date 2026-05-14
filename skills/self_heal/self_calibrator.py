"""自校准器 - 让系统自己调整参数达到目标"""
from lib.memory_simple import memory

class SelfCalibratorSkill:
    name = "self_calibrator"
    description = "系统自校准"
    version = "1.0.0"
    category = "quality"

    def execute(self, params):
        target_duration = params.get("target_duration", 60)
        actual_duration = params.get("actual_duration", 0)
        script_length = params.get("script_length", 0)
        topic = params.get("topic", "")
        
        if actual_duration == 0:
            return {"need_adjust": False}
        
        # 计算偏差
        deviation = actual_duration - target_duration
        deviation_rate = deviation / target_duration
        
        # 根据偏差调整字数目标
        # 公式: 目标字数 = 当前字数 * (目标时长 / 实际时长)
        if deviation_rate > 0.2 or deviation_rate < -0.2:
            adjusted_length = int(script_length * (target_duration / actual_duration))
            adjusted_length = max(50, min(800, adjusted_length))
            
            memory.remember(
                f"校准|{topic}|目标{target_duration}s|实际{actual_duration}s|偏差{deviation_rate:.0%}|建议字数{adjusted_length}",
                category="calibration_log"
            )
            
            return {
                "need_adjust": True,
                "adjusted_script_length": adjusted_length,
                "reason": f"时长偏差{deviation_rate:.0%}"
            }
        
        return {"need_adjust": False, "message": "时长符合目标"}

skill = SelfCalibratorSkill()
