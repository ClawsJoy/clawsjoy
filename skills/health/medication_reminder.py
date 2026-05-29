"""用药提醒"""
class MedicationReminderSkill:
    def execute(self, params):
        name = params.get('name', '')
        time = params.get('time', '')
        dosage = params.get('dosage', '')
        return {"success": True, "message": f"已设置{name}用药提醒: {time} 服用{dosage}"}
skill = MedicationReminderSkill()
