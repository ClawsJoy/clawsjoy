import requests

class HotScriptSkill:
    name = "hot_script"
    description = "基于热点信号生成尖锐脚本"
    version = "1.0.0"
    category = "script"

    def execute(self, params):
        topic = params.get("topic", "香港高才通")
        
        prompt = f"""请根据以下从新闻中提取的热点信号，为「{topic}」主题撰写一个尖锐、有冲击力的短视频脚本。

**必须使用的热点信号（至少选择一条作为脚本核心）:**
- "高才通續簽僅一半、批核94%仍留唔到人"
- "高才通詐騙案大曝光，中介費高達250萬港元"
- "13人伪造文件申请被捕"
- "续签高才通者三分之一不在香港常住"

**核心要求:**
1.  **尖锐开场**: 用提问或数据制造焦虑，直接切入最尖锐的热点。
2.  **数据冲击**: 至少使用上述热点中的两个关键数据。
3.  **真实案例**: 引用上面的诈骗案或伪造文件案作为案例。
4.  **结构**: 尖锐开场 → 数据冲击 → 真实案例 → 行动建议 → 开放式结尾。

**脚本要求:**
- 时长: 60-90秒。
- 形式: 纯旁白脚本。
- 目标: 引发讨论，让观众在评论区留下观点。

请直接输出脚本。
"""
        resp = requests.post("http://127.0.0.1:11434/api/generate",
                             json={"model": "qwen2.5:7b", "prompt": prompt, "stream": False})
        script = resp.json()["response"]
        return {"success": True, "script": script}

skill = HotScriptSkill()
