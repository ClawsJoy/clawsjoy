"""学习进度跟踪"""
class TrackProgressSkill:
    def execute(self, params):
        subject = params.get('subject', 'math')
        completed = params.get('completed', 0)
        total = params.get('total', 100)
        
        progress = completed / total if total > 0 else 0
        return {
            "success": True,
            "progress": f"{progress*100:.0f}%",
            "remaining": total - completed,
            "message": f"{subject}完成{completed}/{total}"
        }
skill = TrackProgressSkill()
