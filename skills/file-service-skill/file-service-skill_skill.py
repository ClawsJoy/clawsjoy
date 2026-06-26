"""文件服务"""
import os, json

class file_service_skill:
    name = "file-service-skill"
    description = "文件读写服务"
    version = "1.0.0"
    
    def execute(self, params):
        action = params.get("action", "read")
        path = params.get("path", "")
        if action == "read" and os.path.exists(path):
            with open(path) as f:
                return {"success": True, "content": f.read()[:5000]}
        elif action == "write":
            with open(path, 'w') as f:
                f.write(params.get("content", ""))
            return {"success": True}
        return {"success": False, "error": "不支持的操作"}
