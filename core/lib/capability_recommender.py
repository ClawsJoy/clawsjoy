#!/usr/bin/env python3
"""能力推荐器 - LLM 推荐 Top 3 能力"""

import requests
import re
import hashlib
import time
from typing import List, Dict, Any
from core.lib.unified_capability_loader import unified_capability_loader


class CapabilityRecommender:
    """LLM 驱动的能力推荐器"""

    def __init__(self, model: str = "qwen2:1.5b-instruct"):
        self.model = model
        self.llm_url = "http://localhost:11434/api/generate"
        self._cache = {}
        self._cache_ttl = 3600  # 1小时

    def recommend(self, user_input: str, types: List[str] = None, n: int = 3) -> List[Dict[str, Any]]:
        """推荐 Top N 个能力"""
        all_caps = unified_capability_loader.load_all()
        if not all_caps:
            print("[Recommender] 没有加载到任何能力")
            return []

        prompt = self._build_prompt(user_input, all_caps, types)
        print(f"[Recommender] 请求 LLM 推荐: {user_input[:50]}...")

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

            names = self._parse_recommendations(response_text)

            results = []
            for name in names:
                name_lower = name.lower()
                for cap_name, cap_data in all_caps.items():
                    if name_lower == cap_name.lower() or name_lower in cap_name.lower() or cap_name.lower() in name_lower:
                        results.append(cap_data)
                        break
                if len(results) >= n:
                    break

            return results[:n]

        except Exception as e:
            print(f"[Recommender] 推荐失败: {e}")
            return []

    def recommend_with_cache(self, user_input: str, types: List[str] = None, n: int = 3) -> List[Dict]:
        """带缓存的推荐"""
        clean_input = " ".join(user_input.strip().split())
        cache_key = hashlib.md5(f"{clean_input}:{str(types)}:{n}".encode()).hexdigest()

        if cache_key in self._cache:
            cached_time, cached_result = self._cache[cache_key]
            if time.time() - cached_time < self._cache_ttl:
                print(f"[Recommender] 命中缓存: {user_input[:30]}...")
                return cached_result

        result = self.recommend(user_input, types, n)
        self._cache[cache_key] = (time.time(), result)
        return result

    def clear_cache(self):
        self._cache.clear()
        print("[Recommender] 缓存已清空")

    def _build_prompt(self, user_input: str, all_caps: Dict, types: List[str] = None) -> str:
        prompt = f"""用户请求: {user_input}

请从以下能力中选择最合适的 {3} 个，按优先级排序。

可用能力列表（必须从中选择）:
"""
        # 只取前 30 个，避免 Token 过多
        sorted_caps = list(all_caps.items())[:30]
        for name, cap in sorted_caps:
            desc = cap.get('description', '')[:60]
            prompt += f"- {name}: {desc}\n"
        prompt += f"\n（共 {len(all_caps)} 个能力，已展示前 30 个）\n"

        prompt += """
请只输出能力名称，用逗号分隔，最多 3 个。
必须使用上面列表中的精确名称。

推荐结果:"""
        return prompt

    def _parse_recommendations(self, text: str) -> List[str]:
        text = re.sub(r'推荐结果[:：]?', '', text)
        text = re.sub(r'推荐[:：]?', '', text)
        text = text.strip()

        names = re.split(r'[,，、\n]', text)

        cleaned = []
        for name in names:
            name = name.strip()
            name = re.sub(r'^\d+[\.、]\s*', '', name)
            name = re.sub(r'\s+', ' ', name)
            if name and len(name) < 60 and not name.startswith('```'):
                cleaned.append(name)

        return cleaned[:5]


# 全局实例
capability_recommender = CapabilityRecommender()
