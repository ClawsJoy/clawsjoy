"""Billing 技能 - 标准格式"""

from typing import Dict
from skills.skill_interface import BaseSkill
import os
import requests

class BillingSkill(BaseSkill):
    name = "billing"
    description = "计费和账单管理"
    version = "1.0.0"
    category = "api"
    
    def execute(self, params: Dict) -> Dict:
        action = params.get("action")
        tenant_id = params.get("tenant_id", "1")
        base_url = os.getenv("BILLING_API_URL", "http://localhost:8090")
        
        if action == "balance":
            resp = requests.get(f'{base_url}/api/billing/balance?tenant_id={tenant_id}')
            return resp.json()
        elif action == "usage":
            resp = requests.get(f'{base_url}/api/billing/usage?tenant_id={tenant_id}')
            return resp.json()
        else:
            return {"error": f"Unknown action: {action}"}

skill = BillingSkill()
