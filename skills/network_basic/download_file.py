"""下载文件"""
import requests
class DownloadFileSkill:
    def execute(self, params):
        url = params.get('url', '')
        try:
            resp = requests.get(url, timeout=30)
            return {"success": True, "size": len(resp.content), "content_type": resp.headers.get('content-type')}
        except Exception as e:
            return {"success": False, "error": str(e)}
skill = DownloadFileSkill()
