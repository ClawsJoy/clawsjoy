#!/usr/bin/env python3
"""能力推荐器 - LLM 推荐 Top 3 能力"""

import requests
import re
from typing import List, Dict, Any
from core.lib.unified_capability_loader import unified_capability_loader


class CapabilityRecommender:
    """LLM 驱动的能力推荐器"""

    def __init__(self, model: str = "qwen2.5:3b"):
        self.model = model
        self.llm_url = "http://localhost:11434/api/generate"

    def recommend(self, user_input: str, types: List[str] = None, n: int = 3) -> List[Dict[str, Any]]:
        """推荐 Top N 个能力"""
        # 1. 获取所有能力
        all_caps = unified_capability_loader.load_all()
        if not all_caps:
            print("[Recommender] 没有加载到任何能力")
            return []

        # 2. 生成提示词
        prompt = self._build_prompt(user_input, all_caps, types)
        print(f"[Recommender] 请求 LLM 推荐: {user_input[:50]}...")

        # 3. 调用 LLM
        try:
            resp = requests.post(
                self.llm_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.2, "num_predict": 100}
                },
                timeout=30
            )

            if resp.status_code != 200:
                print(f"[Recommender] LLM 调用失败: {resp.status_code}")
                return []

            response_text = resp.json().get("response", "").strip()
            print(f"[Recommender] LLM 响应: {response_text}")

            # 4. 解析推荐结果
            names = self._parse_recommendations(response_text)

            # 5. 匹配能力
            results = []
            for name in names:
                # 精确匹配
                if name in all_caps:
                    results.append(all_caps[name])
                    continue

                # 模糊匹配（小写包含）
                name_lower = name.lower()
                for cap_name, cap_data in all_caps.items():
                    if name_lower == cap_name.lower():
                        results.append(cap_data)
                        break
                    elif name_lower in cap_name.lower() or cap_name.lower() in name_lower:
                        results.append(cap_data)
                        break

                if len(results) >= n:
                    break

            # 如果匹配不到，返回空
            if not results:
                print(f"[Recommender] 未匹配到任何能力，请检查 LLM 返回的名称")

            return results[:n]

        except Exception as e:
            print(f"[Recommender] 推荐失败: {e}")
            return []

    def _build_prompt(self, user_input: str, all_caps: Dict, types: List[str] = None) -> str:
        """构建推荐提示词"""
        prompt = f"""用户请求: {user_input}

请从以下能力中选择最合适的 {3} 个，按优先级排序。

可用能力列表（必须从中选择）:
"""
        for name, cap in all_caps.items():
            cap_type = cap.get('_type', 'unknown')
            desc = cap.get('description', '')[:80]
            prompt += f"- {name} [{cap_type}]: {desc}\n"

        prompt += """
请只输出能力名称，用逗号分隔，最多 3 个。
必须使用上面列表中的精确名称。
示例: youtube_agent, video_download, file_agent

推荐结果:"""
        return prompt

    def _parse_recommendations(self, text: str) -> List[str]:
        """解析 LLM 返回的能力名称列表"""
        # 移除常见前缀
        text = re.sub(r'推荐结果[:：]?', '', text)
        text = re.sub(r'推荐[:：]?', '', text)
        text = text.strip()

        # 按逗号、换行、中文逗号分割
        names = re.split(r'[,，、\n]', text)

        cleaned = []
        for name in names:
            name = name.strip()
            # 移除序号
            name = re.sub(r'^\d+[\.、]\s*', '', name)
            # 移除多余空格
            name = re.sub(r'\s+', ' ', name)
            if name and len(name) < 60 and not name.startswith('```'):
                cleaned.append(name)

        return cleaned[:5]


# 全局实例
capability_recommender = CapabilityRecommender()
