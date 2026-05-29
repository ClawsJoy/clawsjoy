"""模拟考试"""
class MockTestSkill:
    def execute(self, params):
        subject = params.get('subject', 'math')
        level = params.get('level', 'midterm')
        
        return {
            "success": True,
            "questions": [
                {"id": 1, "question": "示例题目1", "type": "choice"},
                {"id": 2, "question": "示例题目2", "type": "choice"},
                {"id": 3, "question": "示例题目3", "type": "calculation"}
            ],
            "duration": 60,
            "message": f"{subject}{level}模拟试卷已生成"
        }
skill = MockTestSkill()
