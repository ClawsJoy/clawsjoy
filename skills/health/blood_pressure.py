"""血压记录"""
class BloodPressureSkill:
    def execute(self, params):
        systolic = params.get('systolic', 120)
        diastolic = params.get('diastolic', 80)
        return {"success": True, "message": f"血压记录: {systolic}/{diastolic} mmHg"}
skill = BloodPressureSkill()
