"""HTTP GET请求"""
import requests
class HttpGetSkill:
    def execute(self, params):
        url = params.get('url', '')
        try:
            resp = requests.get(url, timeout=10)
            return {"success": True, "status": resp.status_code, "content": resp.text[:500]}
        except Exception as e:
            return {"success": False, "error": str(e)}
skill = HttpGetSkill()
