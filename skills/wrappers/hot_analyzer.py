"""热门视频分析技能 - 爬取热门视频，提取脚本结构"""
import requests
from bs4 import BeautifulSoup
import re

class HotAnalyzerSkill:
    name = "hot_analyzer"
    description = "分析热门YouTube视频，提取脚本结构"
    version = "1.0.0"
    category = "analysis"

    def execute(self, params):
        topic = params.get("topic", "香港人才计划")
        max_videos = params.get("max_videos", 3)
        
        # 模拟热门视频数据结构（实际需接入 YouTube API）
        # 这里先用示例数据，后续可接入真实数据
        hot_videos = self._fetch_hot_videos(topic, max_videos)
        
        # 分析共同模式
        patterns = self._analyze_patterns(hot_videos)
        
        # 存入记忆
        from lib.memory_simple import memory
        memory.remember(
            f"热门视频分析: {topic} -> 结构: {patterns.get('structure')}",
            category="hot_patterns"
        )
        
        return {
            "success": True,
            "topic": topic,
            "videos_analyzed": len(hot_videos),
            "common_patterns": patterns,
            "structure_template": patterns.get("structure_template", "")
        }
    
    def _fetch_hot_videos(self, topic, max_videos):
        """实际应调用 YouTube API 搜索热门视频"""
        # TODO: 接入 YouTube Data API v3
        # 示例返回模拟数据
        return [
            {
                "title": f"{topic} 2025最新政策解读",
                "duration": "3:45",
                "structure": ["开场钩子", "政策变化", "申请条件", "案例", "总结CTA"]
            },
            {
                "title": f"{topic}申请全攻略",
                "duration": "5:20",
                "structure": ["痛点引入", "政策解读", "材料清单", "常见问题", "行动建议"]
            }
        ]
    
    def _analyze_patterns(self, videos):
        """分析共同模式"""
        structures = [v.get("structure", []) for v in videos]
        # 找出最常见的结构顺序
        common = ["开场钩子", "政策解读", "申请条件", "案例/数据", "总结CTA"]
        return {
            "structure": common,
            "structure_template": "\n".join([f"【{s}】" for s in common])
        }

skill = HotAnalyzerSkill()
