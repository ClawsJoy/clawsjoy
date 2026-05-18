"""大脑调度器 - 增强版"""
import json
import re
import sys
from lib.smart_config import smart_config
sys.path.insert(0, 'str(smart_config.ROOT)')

from lib.smart_adapter import smart_adapter
from lib.skill_loader_v3 import skill_loader
from lib.memory_vector import vector_memory

class DoAnythingSkill:
    name = "do_anything"
    description = "智能大脑：自主规划并组合技能完成任务"
    version = "3.2.0"
    category = "orchestrator"

    def execute(self, params):
        goal = params.get("goal", "")
        if not goal:
            return {"success": False, "error": "需要提供目标"}

        print(f"🧠 大脑收到: {goal}")

        # 1. 数学计算
        math_result = self._quick_math(goal)
        if math_result:
            return math_result

        # 2. 记忆查询（优先）
        if any(kw in goal for kw in ['查询', '搜索', '查', '看', '架构', '改进', 'todo', '成功率', '统计']):
            return self._query_memory(goal)

        # 3. 报告生成
        if any(kw in goal for kw in ['报告', 'PPT', 'PDF']):
            return self._generate_report(goal)

        # 4. 默认
        return self._llm_plan(goal)

    def _quick_math(self, goal):
        match = re.search(r'(\d+)\s*[\+\-\*\/]\s*(\d+)', goal)
        if not match:
            return None
        a, b = int(match.group(1)), int(match.group(2))
        if '+' in goal:
            return {"success": True, "result": a + b, "expression": f"{a} + {b} = {a + b}"}
        if '-' in goal:
            return {"success": True, "result": a - b, "expression": f"{a} - {b} = {a - b}"}
        return None

    def _query_memory(self, goal):
        """查询向量记忆"""
        try:
            from skills.memory.memory_query import skill as memory_skill
            
            # 提取查询关键词
            query = goal
            for w in ['查询', '搜索', '帮我', '查一下', '看看', '请问', '系统', '什么', '是', '多少']:
                query = query.replace(w, '')
            query = query.strip()
            
            if not query or len(query) < 2:
                # 根据内容推断
                if '成功率' in goal:
                    query = '成功率'
                elif '架构' in goal:
                    query = '架构'
                elif 'todo' in goal:
                    query = 'todo'
                else:
                    query = '系统'
            
            print(f"📚 搜索记忆: {query}")
            result = memory_skill.execute({"query": query, "n": 10})
            
            return {
                "success": True,
                "query": query,
                "count": len(result.get('results', [])),
                "results": result.get('results', [])
            }
        except Exception as e:
            return {"success": False, "error": f"记忆查询失败: {e}"}

    def _generate_report(self, goal):
        topic = goal.replace('生成', '').replace('报告', '').replace('PPT', '').strip()
        if not topic:
            topic = "系统报告"
        from skills.memory.memory_query import skill as memory_skill
        result = memory_skill.execute({"query": topic, "n": 10})
        return {"success": True, "topic": topic, "memories": len(result.get('results', []))}

    def _llm_plan(self, goal):
        skills = skill_loader.list_skills()[:20]
        prompt = f"目标:{goal}\n可用技能:{skills}\n输出JSON:{{\"skill\":\"技能名\",\"params\":{{}}}}"
        response = smart_adapter.generate(prompt, auto_select=True)
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            try:
                plan = json.loads(match.group())
                skill_name = plan.get("skill")
                params = plan.get("params", {})
                if skill_name:
                    result = skill_loader.execute(skill_name, params)
                    return result
            except:
                pass
        return {"success": False, "error": "无法执行任务"}

skill = DoAnythingSkill()
