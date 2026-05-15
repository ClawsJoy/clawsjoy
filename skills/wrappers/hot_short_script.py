import requests
import re

class HotShortScriptSkill:
    name = "hot_short_script"
    description = "基于热点生成60秒纯旁白脚本"
    version = "1.0.0"
    category = "script"

    def execute(self, params):
        topic = params.get("topic", "高才通续签")
        
        prompt = f"""为「{topic}」生成一个60秒的纯旁白脚本。

**严格禁止：**
- 不要任何镜头描述（不要【】、不要[]、不要“镜头”二字）
- 不要角色标注（不要“旁白：”）
- 不要分隔符（不要“---”、不要“**”）

**要求：**
- 只输出纯文本旁白内容
- 用「有数据表明」、「更令人震惊的是」、「举个例子」等连接词过渡
- 黄金3秒开场
- 至少使用两个热点数据
- 开放式结尾引导评论

**热点素材：**
- 续签率仅一半，94%获批者却不在香港常住
- 13人伪造文件被捕，中介费250万港元

直接输出旁白文本：
"""
        resp = requests.post("http://127.0.0.1:11434/api/generate",
                             json={"model": "qwen2.5:7b", "prompt": prompt, "stream": False})
        script = resp.json()["response"]
        
        # 清理可能残留的标记
        script = re.sub(r'【.*?】|\[.*?\]|旁白[：:]|镜头\d|\(.*?\)', '', script)
        script = re.sub(r'\n{3,}', '\n\n', script)
        
        return {"success": True, "script": script.strip()}

skill = HotShortScriptSkill()
