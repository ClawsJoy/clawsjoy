"""
下载文件
"""
class Download_fileSkill:
    name = "download_file"
    description = "下载文件"
    version = "1.0.0"
    category = "network"
    
    def execute(self, params):
        import requests; url = params.get('url'); path = params.get('path'); response = requests.get(url, timeout=60); Path(path).write_bytes(response.content); result = f'下载完成: {path}'
        return {"success": True, "result": result}

skill = Download_fileSkill()
