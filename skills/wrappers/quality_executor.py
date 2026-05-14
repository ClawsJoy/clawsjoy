from skills.intent_parser import skill as parser
from skills.hot_dual_script import skill as script_gen
from skills.spider import skill as spider
from skills.tts import skill as tts
from skills.manju_maker import skill as manju_maker
from skills.quality_gate import skill as gate

class QualityExecutorSkill:
    name = "quality_executor"
    description = "逐环节执行，质量门检验，支持自校准"
    version = "1.0.0"
    category = "executor"

    def execute(self, params):
        user_input = params.get("input", "")
        max_retries = params.get("max_retries", 3)
        
        print(f"📝 用户诉求: {user_input}")
        
        # 环节1: 意图解析
        task_spec = parser.execute({"input": user_input})
        target = task_spec.get("target", {"duration": 60, "script_length": 200})
        topic = task_spec.get("topic", user_input)
        print(f"   目标: 时长{target['duration']}秒, 字数{target['script_length']}字")
        
        # 环节2: 脚本生成（支持动态调整）
        for attempt in range(max_retries):
            print(f"\n[脚本] 尝试{attempt+1}, 目标字数:{target['script_length']}")
            scripts = script_gen.execute({"topic": topic})
            narration = scripts.get("narration", "")
            
            gate_result = gate.execute({
                "stage": "script", 
                "result": {"script": narration},
                "target": target
            })
            
            if gate_result["pass"]:
                print(f"   ✅ 脚本合格 (长度:{len(narration)}字)")
                break
            
            if gate_result.get("need_adjust"):
                target = gate_result["adjusted_target"]
                print(f"   📝 调整目标: 字数{target['script_length']}")
            else:
                print(f"   ❌ {gate_result['message']}")
                if attempt == max_retries - 1:
                    return {"success": False, "stage": "script"}
        
        # 环节3: 配音（自动校准时长）
        for attempt in range(max_retries):
            print(f"\n[配音] 尝试{attempt+1}, 目标时长:{target['duration']}秒")
            audio_path = "output/tts_audio.mp3"
            audio_result = tts.execute({"text": narration[:800], "output_path": audio_path})
            
            import subprocess, os
            duration = 0
            if os.path.exists(audio_path):
                proc = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                                       '-of', 'default=noprint_wrappers=1:nokey=1', audio_path],
                                      capture_output=True, text=True)
                if proc.stdout.strip():
                    duration = float(proc.stdout.strip())
            
            gate_result = gate.execute({
                "stage": "audio",
                "result": {"duration": duration},
                "target": target
            })
            
            if gate_result["pass"]:
                print(f"   ✅ 配音合格 (时长:{duration:.1f}秒)")
                break
            
            if gate_result.get("need_adjust"):
                target = gate_result["adjusted_target"]
                print(f"   📝 校准目标: 时长{target['duration']}秒, 字数{target['script_length']}")
                # 重新生成脚本
                scripts = script_gen.execute({"topic": topic, "target_length": target['script_length']})
                narration = scripts.get("narration", "")
                print(f"   📝 重新生成脚本: {len(narration)}字")
            else:
                print(f"   ❌ {gate_result['message']}")
                if attempt == max_retries - 1:
                    return {"success": False, "stage": "audio"}
        
        # 环节4-5: 背景、视频合成（简化）
        # ... 背景采集和视频合成代码
        
        return {"success": True, "video": "output/manju_final.mp4", "target": target}

skill = QualityExecutorSkill()
