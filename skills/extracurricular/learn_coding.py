"""编程入门"""
class LearnCodingSkill:
    def execute(self, params):
        language = params.get('language', 'python')
        level = params.get('level', 'beginner')
        
        lessons = {
            "python": ["打印输出", "变量", "条件判断", "循环", "函数"],
            "scratch": ["角色移动", "事件触发", "变量控制", "克隆", "广播"]
        }
        content = lessons.get(language, lessons["python"])
        return {"success": True, "lessons": content, "message": f"{language}入门课程 {level}级"}
skill = LearnCodingSkill()
