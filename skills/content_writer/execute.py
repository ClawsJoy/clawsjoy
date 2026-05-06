#!/usr/bin/env python3
"""写YouTube视频脚本"""
import sys, json, requests

def execute(params):
    topic = params.get("topic", "")
    duration = params.get("duration", 3)
    
    prompt = f"""写一个关于「{topic}」的{duration}分钟YouTube视频脚本。
要求：口语化、有开场/正文/结尾、直接输出脚本内容。"""
    
    try:
        resp = requests.post("http://localhost:8101/api/agent",
            json={"text": prompt}, timeout=90)
        if resp.status_code == 200:
            script = resp.json().get("message", "")
            return {"success": True, "script": script, "topic": topic}
    except Exception as e:
        return {"success": False, "error": str(e)}
    return {"success": False, "error": "生成失败"}

if __name__ == "__main__":
    params = json.loads(sys.argv[1])
    print(json.dumps(execute(params)))
