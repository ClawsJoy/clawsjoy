"""UUID 生成技能"""
import uuid

class UuidGenSkill:
    name = "uuid_gen"
    description = "生成 UUID"
    version = "1.0.0"
    category = "tools"
    
    def execute(self, params):
        version = params.get("version", 4)
        
        if version == 1:
            result = str(uuid.uuid1())
        elif version == 4:
            result = str(uuid.uuid4())
        else:
            result = str(uuid.uuid4())
        
        return {"success": True, "result": result}

skill = UuidGenSkill()
