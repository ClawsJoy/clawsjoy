#!/usr/bin/env python3
"""租户专属 Agent - 管家模式"""

import json
import re
from pathlib import Path

class TenantAgent:
    
    def __init__(self, tenant_id):
        self.tenant_id = tenant_id
        self.config_dir = Path(f"/mnt/d/clawsjoy/tenants/{tenant_id}/agent")
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.load_state()
    
    def load_state(self):
        state_file = self.config_dir / "state.json"
        if state_file.exists():
            with open(state_file) as f:
                self.state = json.load(f)
        else:
            self.state = {
                "tenant_id": self.tenant_id,
                "youtube_configured": False,
                "created_at": __import__('datetime').datetime.now().isoformat()
            }
    
    def save_state(self):
        state_file = self.config_dir / "state.json"
        with open(state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def collect_keywords(self, text):
        """从用户对话中采集新关键词"""
        patterns = [
            r'(?:关于|聊|讲|说|什么是?|了解)([^，,。？?！!]{2,10})',
            r'([\u4e00-\u9fa5]{2,6})(?:计划|政策|申请|流程|条件)',
        ]
        
        new_keywords = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            new_keywords.extend(matches)
        
        if new_keywords:
            kw_file = self.config_dir / "keywords.json"
            if kw_file.exists():
                with open(kw_file) as f:
                    keywords = json.load(f)
            else:
                keywords = []
            
            for kw in new_keywords:
                if kw not in keywords:
                    keywords.append(kw)
            
            with open(kw_file, 'w') as f:
                json.dump(keywords, f, ensure_ascii=False, indent=2)
            
            print(f"📝 采集到新关键词: {new_keywords}")
        
        return new_keywords
    
    def chat(self, user_input):
        """主对话方法 - 增强版包含关键词采集"""
        # 采集关键词
        self.collect_keywords(user_input)
        
        # 密钥识别、意图路由、脱敏处理等
        user_lower = user_input.lower()
        
        if "youtube" in user_lower and "配置" in user_lower:
            return {"action": "configure_youtube", "message": "请提供 client_secrets.json 文件路径"}
        
        if "上传" in user_lower and "视频" in user_lower:
            return {"action": "upload_video", "message": "正在上传视频..."}
        
        return {"action": "chat", "message": f"收到：{user_input}"}

def get_agent(tenant_id):
    return TenantAgent(tenant_id)

if __name__ == "__main__":
    agent = TenantAgent("tenant_1")
    print(agent.chat("关于香港优才计划"))
    print(agent.chat("上传视频"))
