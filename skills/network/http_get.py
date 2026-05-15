"""
HTTP GET请求
"""
class Http_getSkill:
    name = "http_get"
    description = "HTTP GET请求"
    version = "1.0.0"
    category = "network"
    
    def execute(self, params):
        import requests; url = params.get('url'); response = requests.get(url, timeout=30); result = response.text
        return {"success": True, "result": result}

skill = Http_getSkill()
