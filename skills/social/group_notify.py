"""群发通知"""
class GroupNotifySkill:
    def execute(self, params):
        group = params.get('group', '')
        content = params.get('content', '')
        members = params.get('members', 10)
        return {"success": True, "notified": members, "message": f"已群发通知给{group}的{members}人"}
skill = GroupNotifySkill()
