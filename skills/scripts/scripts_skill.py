"""脚本管理"""
import os
class scripts:
    name = "scripts"
    description = "脚本管理"
    version = "1.0.0"
    def execute(self, params):
        d = "scripts"
        if os.path.exists(d):
            return {"success": True, "scripts": [f for f in os.listdir(d) if f.endswith('.py')]}
        return {"success": True, "scripts": []}
