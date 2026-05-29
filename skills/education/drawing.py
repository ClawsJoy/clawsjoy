"""绘画指导"""
class DrawingSkill:
    def execute(self, params):
        subject = params.get('subject', 'cat')
        steps = [
            f"1. 画一个圆作为{subject}的头部",
            f"2. 画两个三角形作为耳朵",
            f"3. 画眼睛和鼻子",
            f"4. 画身体和尾巴"
        ]
        return {"success": True, "steps": steps, "message": f"教你画{subject}"}
skill = DrawingSkill()
