#!/usr/bin/env python3
"""Learn Chinese - Learn Chinese 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

class LearnChineseSkill:
    def execute(self, params):
        grade = params.get('grade', 3)
        content = params.get('content', 'poetry')
        
        poetry = {
            3: ["静夜思", "春晓", "登鹳雀楼"],
            4: ["望庐山瀑布", "绝句", "江雪"],
            5: ["枫桥夜泊", "浪淘沙", "示儿"]
        }
        poems = poetry.get(grade, poetry[3])
        return {"success": True, "poems": poems, "message": f"{grade}年级必背古诗"}
skill = LearnChineseSkill()
