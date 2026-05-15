"""数据分析 Agent"""
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

from agents.base_agent import BaseAgent

class DataAgent(BaseAgent):
    name = "data_agent"
    description = "数据分析专家，处理数据查询、统计、可视化"
    capabilities = ["data_query", "data_analysis", "data_visualization", "report_generation"]
    skills = ["json_parser", "text_processor", "search"]
    
    def execute(self, params):
        operation = params.get("operation")
        data = params.get("data", {})
        
        if operation == "analyze":
            return self._analyze(data)
        elif operation == "query":
            return self._query(params.get("query"))
        elif operation == "report":
            return self._generate_report(data)
        return {"success": False, "error": "未知操作"}
    
    def _analyze(self, data):
        from skills.text_processor import skill
        result = skill.execute({"text": str(data), "operation": "summary"})
        return {"success": True, "analysis": result.get("result")}
    
    def _query(self, query):
        from skills.search import skill
        result = skill.execute({"query": query})
        return {"success": True, "results": result.get("results", [])}
    
    def _generate_report(self, data):
        return {"success": True, "report": f"数据报告: 共 {len(data) if isinstance(data, list) else 1} 项"}

data_agent = DataAgent()
