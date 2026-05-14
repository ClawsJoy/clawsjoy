"""改善执行器 - 大脑调度原子技能执行改善"""
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')
import json
import re
from lib.memory_simple import memory

class ImproveExecutorSkill:
    name = "improve_executor"
    description = "根据分析结果自动执行改善"
    version = "1.0.0"
    category = "improvement"

    def execute(self, params):
        # 获取最新分析
        analysis_list = memory.recall_all(category='unified_analysis')
        if not analysis_list:
            return {"success": False, "message": "无分析结果"}
        
        # 解析分析结果
        match = re.search(r'\{.*\}', analysis_list[-1], re.DOTALL)
        if not match:
            return {"success": False, "message": "解析失败"}
        
        analysis = json.loads(match.group())
        
        executed = []
        
        # 根据关键问题调用原子技能
        issues = analysis.get('critical_issues', [])
        
        for issue in issues:
            if '字幕' in issue:
                executed.append("字幕修复建议: 检查 add_subtitles 时间轴")
            
            if '头像' in issue:
                executed.append("头像优化建议: 重新生成角色头像")
        
        # 记录执行
        memory.remember(
            f"改善执行|{','.join(executed)}",
            category='improvement_history'
        )
        
        return {"success": True, "executed": executed, "issues_found": len(issues)}

skill = ImproveExecutorSkill()
