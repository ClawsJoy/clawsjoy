#!/usr/bin/env python3
"""运维技能库 - 简化版"""

import subprocess

class OpsSkills:
    def __init__(self):
        self.skills = {
            "fix_agent_api": {
                "cmd": "cd /mnt/d/clawsjoy/bin && pm2 start agent_api.py --name agent-api -- --port 18103 2>/dev/null || pm2 restart agent-api",
                "description": "修复 Agent API"
            },
            "fix_chat_api": {
                "cmd": "cd /mnt/d/clawsjoy/bin && pm2 start chat_api.py --name chat-api -- --port 18109 2>/dev/null || pm2 restart chat-api",
                "description": "修复 Chat API"
            },
            "fix_promo_api": {
                "cmd": "cd /mnt/d/clawsjoy/bin && pm2 start promo_api.py --name promo-api -- --port 8108 2>/dev/null || pm2 restart promo-api",
                "description": "修复 Promo API"
            },
            "fix_web": {
                "cmd": "cd /mnt/d/clawsjoy && docker-compose up -d web 2>/dev/null || docker start clawsjoy-web",
                "description": "修复 Web"
            },
            "restart_all": {
                "cmd": "pm2 restart all && pm2 save",
                "description": "重启所有服务"
            }
        }
    
    def execute(self, skill_name):
        if skill_name not in self.skills:
            return {"success": False, "error": f"未知技能: {skill_name}"}
        
        skill = self.skills[skill_name]
        print(f"执行: {skill['description']}")
        
        try:
            result = subprocess.run(skill["cmd"], shell=True, capture_output=True, text=True)
            success = result.returncode == 0
            return {"success": success, "skill": skill_name, "message": f"{skill['description']}: {'成功' if success else '失败'}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def check_all(self):
        results = {}
        # 简化检查：只看 pm2 是否有服务
        result = subprocess.run("pm2 list | grep -q online", shell=True)
        results["services"] = result.returncode == 0
        return results

if __name__ == "__main__":
    ops = OpsSkills()
    print("=== 测试 ===")
    for skill in ["fix_agent_api", "fix_chat_api", "fix_promo_api"]:
        result = ops.execute(skill)
        print(f"{skill}: {result['message']}")
