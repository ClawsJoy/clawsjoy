"""Skill 注册表 - 供大模型调用"""
import json

SKILLS = {
    "make_promo": {
        "description": "制作城市宣传片。当用户要求制作宣传片时调用。",
        "parameters": {
            "city": {"type": "string", "description": "城市名称", "required": True},
            "style": {"type": "string", "description": "风格（科技/复古/温馨）", "default": "科技"}
        }
    },
    "list_photos": {
        "description": "列出资料库中的照片。当用户想看照片时调用。",
        "parameters": {}
    },
    "order_coffee": {
        "description": "订购咖啡。当用户想喝咖啡时调用。",
        "parameters": {
            "item": {"type": "string", "description": "咖啡类型", "required": True}
        }
    }
}

def get_skills_prompt():
    """生成给大模型的 Skills 描述"""
    prompt = "你可以调用以下工具：\n"
    for name, skill in SKILLS.items():
        prompt += f"- {name}: {skill['description']}\n"
        if skill.get('parameters'):
            prompt += f"  参数: {json.dumps(skill['parameters'], ensure_ascii=False)}\n"
    prompt += "\n当用户有相关需求时，请输出 JSON 格式：{\"tool\": \"工具名\", \"params\": {...}}"
    return prompt

def execute_skill(tool_name, params):
    """执行 Skill"""
    if tool_name == "make_promo":
        import requests
        city = params.get('city', '香港')
        style = params.get('style', '科技')
        resp = requests.post("http://redis:8084/api/task/promo",
                            json={'city': city, 'style': style, 'tenant_id': '1'},
                            timeout=60)
        return resp.json()
    elif tool_name == "list_photos":
        import requests
        resp = requests.get("http://redis:8084/api/library/list", params={'tenant_id': '1', 'limit': 5})
        files = resp.json().get('files', [])
        return {"type": "library", "files": [f['name'] for f in files]}
    elif tool_name == "order_coffee":
        import requests
        resp = requests.get("http://redis:8085/api/coffee/shops")
        return resp.json()
    return {"error": "Unknown tool"}
