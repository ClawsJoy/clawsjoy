from lib.unified_config import config
#!/usr/bin/env python3
"""任务编排器 - 基于关键词索引，不依赖大模型"""

import json
import re
import requests
from pathlib import Path

class TaskOrchestrator:
    def __init__(self):
        self.skill_index = self._load_skill_index()
        self.context_index = self._load_context_index()
        self.meilisearch = "http://localhost:7700"
    
    def _load_skill_index(self):
        with open("config.ROOT/data/skill_keywords.json") as f:
            return json.load(f)
    
    def _load_context_index(self):
        with open("config.ROOT/data/skill_keywords.json") as f:
            return json.load(f).get("contexts", [])
    
    def match_skill(self, user_input):
        """根据关键词匹配技能"""
        for skill in self.skill_index["skills"]:
            for kw in skill["keywords"]:
                if kw in user_input:
                    return skill
        return None
    
    def extract_params(self, user_input, skill):
        """提取参数（基于关键词规则）"""
        params = {}
        
        # 提取城市
        for ctx in self.context_index:
            if ctx["id"] == "city":
                for city in ctx["keywords"]:
                    if city in user_input:
                        params["city"] = city
                        break
        
        # 提取时长
        match = re.search(r'(\d+)\s*分钟', user_input)
        if match:
            params["duration"] = int(match.group(1)) * 60
        match = re.search(r'(\d+)\s*秒', user_input)
        if match:
            params["duration"] = int(match.group(1))
        
        # 提取 Webhook URL
        url_match = re.search(r'https?://[^\s]+', user_input)
        if url_match:
            params["webhook_url"] = url_match.group()
        
        # 提取平台
        if "钉钉" in user_input:
            params["platform"] = "dingtalk"
        elif "飞书" in user_input:
            params["platform"] = "feishu"
        elif "企微" in user_input:
            params["platform"] = "wechat"
        
        return params
    
    def build_task(self, user_input):
        """构建任务"""
        skill = self.match_skill(user_input)
        if not skill:
            return None
        
        params = self.extract_params(user_input, skill)
        
        return {
            "skill_id": skill["id"],
            "skill_name": skill["name"],
            "action": skill["action"],
            "params": params,
            "original_input": user_input
        }
    
    def execute_task(self, task):
        """执行任务"""
        skill_id = task["skill_id"]
        params = task["params"]
        
        if skill_id == "generate_video":
            return self._call_promo_api(params)
        elif skill_id == "upload_video":
            return self._call_youtube_upload(params)
        elif skill_id == "config_alert":
            return self._save_webhook(params)
        elif skill_id == "search_knowledge":
            return self._search_qdrant(params)
        elif skill_id == "learn_keyword":
            return self._add_keyword(params)
        
        return {"success": False, "message": f"未知技能: {skill_id}"}
    
    # ========== 技能执行器 ==========
    def _call_promo_api(self, params):
        import requests
        city = params.get("city", "香港")
        duration = params.get("duration", 30)
        try:
            resp = requests.post("http://localhost:8108/api/promo/make",
                                json={"topic": city, "duration": duration},
                                timeout=120)
            return resp.json() if resp.status_code == 200 else {"success": False}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _call_youtube_upload(self, params):
        import subprocess
        result = subprocess.run(
            ["python3", "config.ROOT/agents/youtube_uploader.py", "--tenant", "tenant_1"],
            capture_output=True, text=True, timeout=300
        )
        return {"success": result.returncode == 0, "output": result.stdout}
    
    def _save_webhook(self, params):
        from pathlib import Path
        import json
        webhook_url = params.get("webhook_url")
        platform = params.get("platform", "dingtalk")
        if not webhook_url:
            return {"success": False, "message": "未提供 Webhook URL"}
        
        config_file = Path("config.ROOT/tenants/tenant_1/agent_config.json")
        if config_file.exists():
            with open(config_file) as f:
                config = json.load(f)
        else:
            config = {}
        
        if "alert_webhooks" not in config:
            config["alert_webhooks"] = {}
        config["alert_webhooks"][platform] = webhook_url
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        return {"success": True, "message": f"已配置 {platform} 告警"}
    
    def _search_qdrant(self, params):
        query = params.get("query", "")
        try:
            resp = requests.post("http://localhost:6333/collections/kb_tenant_1/points/search",
                                json={"vector": [0.0]*384, "limit": 3})
            return {"success": True, "results": resp.json() if resp.status_code == 200 else []}
        except:
            return {"success": False, "results": []}
    
    def _add_keyword(self, params):
        keyword = params.get("keyword", "")
        category = params.get("category", "通用")
        if not keyword:
            return {"success": False, "message": "未提供关键词"}
        
        # 添加到关键词库
        kw_file = Path("config.ROOT/data/keywords.json")
        with open(kw_file) as f:
            data = json.load(f)
        
        if category not in data["categories"]:
            data["categories"][category] = {"keywords": [], "weight": 1.0}
        
        if keyword not in data["categories"][category]["keywords"]:
            data["categories"][category]["keywords"].append(keyword)
        
        with open(kw_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        return {"success": True, "message": f"已学习新关键词: {keyword}"}

# 集成到 TenantAgent
class OrchestratorAgent:
    def __init__(self, tenant_id="tenant_1"):
        self.tenant_id = tenant_id
        self.orchestrator = TaskOrchestrator()
    
    def process(self, user_input):
        task = self.orchestrator.build_task(user_input)
        if task:
            print(f"🎯 匹配技能: {task['skill_name']}")
            result = self.orchestrator.execute_task(task)
            return {"type": "result", "message": result.get("message", "完成"), "data": result}
        else:
            return {"type": "text", "message": "未识别到有效指令，请尝试：制作视频、上传视频、配置告警"}

if __name__ == "__main__":
    agent = OrchestratorAgent()
    for test in ["制作深圳宣传片", "上传视频", "配置钉钉告警", "你好"]:
        print(f"\n输入: {test}")
        print(agent.process(test))
