"""
HTTP POST请求
"""
class Http_postSkill:
    name = "http_post"
    description = "HTTP POST请求"
    version = "1.0.0"
    category = "network"
    
    def execute(self, params):
        import requests; url = params.get('url'); data = params.get('data', {}); response = requests.post(url, json=data, timeout=30); result = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        return {"success": True, "result": result}

skill = Http_postSkill()
