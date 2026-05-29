"""生成随机密码"""
import random
import string

class GenPasswordSkill:
    def execute(self, params):
        length = params.get('length', 12)
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(random.choice(chars) for _ in range(length))
        return {"success": True, "password": password}
skill = GenPasswordSkill()
