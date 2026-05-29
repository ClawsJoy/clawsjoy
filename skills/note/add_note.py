"""添加笔记"""
class AddNoteSkill:
    def execute(self, params):
        title = params.get('title', '')
        content = params.get('content', '')
        
        return {
            "success": True,
            "message": f"已添加笔记: {title}",
            "note": {"title": title, "content": content}
        }
skill = AddNoteSkill()
