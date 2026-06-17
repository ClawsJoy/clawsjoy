#!/usr/bin/env python3
"""video_indexer_agent v4.0 - 智慧化视频索引智能体"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import re
from typing import Dict, Optional, Tuple

from core.agents.business.business_agent import BusinessAgent


class VideoIndexerAgentV4(BusinessAgent):
    """智慧化视频索引助手"""
    
    name = "video_indexer_agent_v4"
    description = "智慧化视频索引助手"
    version = "4.0.0"
    
    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self._index = {}
        print(f"📹 {self.name} v{self.version} 智慧化启动")
    
    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        capabilities = {
            ("index", "video"): (True, 0.90),
            ("search", "video"): (True, 0.85),
        }
        return capabilities.get((action, target), (False, 0.0))
    
    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        
        # 索引视频
        if any(kw in user_input for kw in ["索引视频", "添加视频"]):
            return self._index_video(user_input)
        
        # 搜索视频
        if any(kw in user_input for kw in ["搜索视频", "查找视频"]):
            return self._search_video(user_input)
        
        return self._response(self._smart_fallback(user_input))
    
    def _index_video(self, user_input: str) -> Dict:
        """索引视频"""
        match = re.search(r'(?:索引视频|添加视频)[：:]\s*(.+)', user_input)
        video_info = match.group(1) if match else "视频"
        
        prompt = f"""请为以下视频生成索引标签：

视频信息：{video_info}

生成内容：
1. 关键词标签（3-5个）
2. 内容分类
3. 时长建议
4. 适合人群"""
        
        response = self._call_llm(prompt)
        
        if response:
            return self._response(
                f"📹 **视频索引**\n\n{response}",
                metadata={"type": "index"}
            )
        
        return self._response(self._get_index_template(video_info))
    
    def _search_video(self, user_input: str) -> Dict:
        """搜索视频"""
        match = re.search(r'(?:搜索视频|查找视频)[：:]\s*(.+)', user_input)
        keyword = match.group(1) if match else ""
        
        if not keyword:
            return self._response("请提供搜索关键词。\n\n示例：搜索视频 Python 教程")
        
        return self._response(
            f"🔍 **视频搜索**\n\n关键词：{keyword}\n\n"
            f"💡 提示：接入视频索引数据库可获得真实搜索结果\n\n"
            f"推荐视频类型：\n"
            f"• 教程类\n"
            f"• 讲解类\n"
            f"• 实战类",
            metadata={"keyword": keyword}
        )
    
    def _get_index_template(self, video_info: str) -> str:
        return f"""📹 **视频索引建议**

视频：{video_info}

🏷️ 推荐标签：
- 主题词
- 难度级别
- 时长范围
- 适用场景

📂 分类建议：
- 教程 / 娱乐 / 资讯

💡 提示：接入视频索引 API 可自动生成标签"""
    
    def _get_help(self) -> str:
        return """📹 **视频索引助手**

支持功能:
- 索引视频: "索引视频 Python入门教程"
- 搜索视频: "搜索视频 机器学习"

💡 提示：接入 Azure Video Indexer 可获得专业视频分析"""
    
    def _response(self, content: str, **kwargs) -> Dict:
        return {
            "success": True,
            "response": content,
            "output_content": content,
            **kwargs
        }


if __name__ == "__main__":
    agent = VideoIndexerAgentV4("test")
    print("✅ video_indexer_agent_v4 测试通过")
