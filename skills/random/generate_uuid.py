"""生成UUID"""
import uuid
class GenerateUuidSkill:
    def execute(self, params):
        count = params.get('count', 1)
        uuids = [str(uuid.uuid4()) for _ in range(count)]
        return {"success": True, "uuids": uuids if count > 1 else uuids[0]}
skill = GenerateUuidSkill()
