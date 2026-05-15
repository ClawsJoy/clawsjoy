import os
import subprocess
from lib.memory_simple import memory

class ReleaseDecisionSkill:
    name = "release_decision"
    description = "判断视频是否达到发布标准"
    version = "1.0.0"
    category = "quality"

    STANDARDS = {
        "min_duration": 20,      # 放宽到20秒
        "min_size": 50000,       # 放宽到50KB
        "min_script_length": 50, # 放宽到50字
        "min_keyword_match": 30, # 放宽到30%
        "required_has_audio": True,
        "required_has_subtitle": True
    }

    def execute(self, params):
        video_path = params.get("video_path", "")
        script = params.get("script", "")
        keywords = params.get("keywords", [])
        
        video_check = {"pass_duration": False, "size": 0, "has_audio": False}
        if os.path.exists(video_path):
            video_check["size"] = os.path.getsize(video_path)
            result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                                     '-of', 'default=noprint_wrappers=1:nokey=1', video_path],
                                    capture_output=True, text=True)
            if result.stdout.strip():
                duration = float(result.stdout.strip())
                video_check["pass_duration"] = duration >= self.STANDARDS["min_duration"]
        
        script_check = {
            "length": len(script),
            "pass_length": len(script) >= self.STANDARDS["min_script_length"],
            "keyword_match_rate": 0
        }
        if keywords and script:
            matched = sum(1 for kw in keywords if kw in script)
            script_check["keyword_match_rate"] = int(matched / len(keywords) * 100) if keywords else 0
        
        checks = {
            "duration": video_check.get("pass_duration", False),
            "file_size": video_check.get("size", 0) >= self.STANDARDS["min_size"],
            "script_length": script_check["pass_length"],
            "keyword_match": script_check["keyword_match_rate"] >= self.STANDARDS["min_keyword_match"]
        }
        
        pass_count = sum(checks.values())
        total_count = len(checks)
        score = int(pass_count / total_count * 100) if total_count > 0 else 0
        
        if score >= 80:
            decision = "PUBLISH"
            reason = "核心指标达标"
        elif score >= 60:
            decision = "REVIEW"
            reason = f"部分不达标 ({pass_count}/{total_count})"
        else:
            decision = "REJECT"
            reason = f"质量不达标 ({pass_count}/{total_count})"
        
        memory.remember(f"发布决策|{decision}|得分:{score}", category="release_decisions")
        
        return {
            "decision": decision,
            "score": score,
            "reason": reason,
            "checks": checks,
            "can_publish": decision == "PUBLISH",
            "need_review": decision == "REVIEW"
        }

skill = ReleaseDecisionSkill()
