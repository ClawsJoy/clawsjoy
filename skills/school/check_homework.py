"""查看作业"""
class CheckHomeworkSkill:
    def execute(self, params):
        date = params.get('date', 'today')
        homework = {
            "语文": "背诵古诗一首",
            "数学": "练习册P20-25",
            "英语": "单词抄写5遍"
        }
        return {"success": True, "homework": homework, "message": f"{date}作业列表"}
skill = CheckHomeworkSkill()
