import sys
sys.path.insert(0, '/mnt/d/clawsjoy')
import json
import requests
import re
from lib.data_contract import DataContract

class SelfDesignerV4Skill:
    name = "self_designer_v4"
    description = "根据分析结果自动设计方案（使用现有技能）"
    version = "1.0.0"
    category = "design"

    # 现有技能映射
    SKILL_MAP = {
        '抠图': 'character_designer (自动生成透明背景头像)',
        '字幕': 'add_subtitles (自动添加字幕)',
        '图片': 'spider (采集图片)',
        '语音': 'tts (文字转语音)',
        '视频': 'manju_maker (一键制作漫剧)'
    }

    def execute(self, params):
        analysis = DataContract.get_latest_analysis()
        if not analysis:
            return {"success": False, "message": "无分析结果"}
        
        issues = analysis.get('critical_issues', [])
        designs = []
        
        for issue in issues:
            design = self._match_skill(issue)
            designs.append({"issue": issue, "design": design})
        
        DataContract.store_design(designs)
        return {"success": True, "designs": designs, "issues_found": len(issues)}
    
    def _match_skill(self, issue):
        """匹配现有技能"""
        for keyword, skill_name in self.SKILL_MAP.items():
            if keyword in issue:
                return {
                    "skill_chain": [skill_name.split('(')[0].strip()],
                    "parameters": {},
                    "expected_result": f"使用 {skill_name} 解决 {issue}"
                }
        return {"skill_chain": ["manual_fix"], "parameters": {}, "expected_result": "需要手动处理"}

skill = SelfDesignerV4Skill()
