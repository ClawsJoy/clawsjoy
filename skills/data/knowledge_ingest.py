"""知识入库技能 - 采集并向量化存储"""
import json
from pathlib import Path
from lib.memory_simple import memory

class KnowledgeIngestSkill:
    name = "knowledge_ingest"
    description = "采集网页知识并入库"
    version = "1.0.0"
    category = "knowledge"

    def execute(self, params):
        url = params.get("url", "")
        topic = params.get("topic", "general")
        content = params.get("content", "")
        
        if not url and not content:
            return {"error": "需要 url 或 content"}
        
        # 如果有 URL，先采集
        if url and not content:
            from skills.spider import skill as spider
            result = spider.execute({'mode': 'webpage', 'url': url})
            if not result.get('success'):
                return {"error": "采集失败"}
            title = result.get('title', '')
            content = result.get('content', '')
            url = result.get('url', url)
        else:
            title = params.get("title", "")
        
        # 存入记忆（关键词检索）
        memory.remember(
            f"【{topic}】{title}: {content[:800]}",
            category=f"knowledge_{topic}"
        )
        
        # 同时存入通用知识库
        memory.remember(
            f"知识: {title} - {content[:300]}",
            category="knowledge_general"
        )
        
        return {
            "success": True,
            "topic": topic,
            "title": title,
            "content_length": len(content),
            "source": url
        }

skill = KnowledgeIngestSkill()
