"""Soul 注入器 - 身份 + 价值观 + 情感"""

from pathlib import Path
import json
import random
from datetime import datetime
from typing import Dict, Tuple


class SoulInjector:
    def __init__(self, user_id: str, agent_name: str):
        self.user_id = user_id
        self.agent_name = agent_name
        self._load_relationship()
        self._init_emotion()
    
    def _init_emotion(self):
        """初始化情绪状态"""
        self.emotion = {
            "energy": 0.8,           # 精力 (0-1)
            "warmth": 0.3,           # 温暖度 (0-1)
            "curiosity": 0.5,        # 好奇心 (0-1)
            "last_sentiment": None   # 用户最后情绪
        }
    
    def _load_relationship(self):
        path = Path(f"data/relationship/{self.user_id}.json")
        if path.exists():
            try:
                with open(path, 'r') as f:
                    self.data = json.load(f)
                return
            except:
                pass
        self.data = {
            "first_met": datetime.now().isoformat(),
            "interaction_count": 0,
            "user_name": None,
            "values": {
                "helpful": 0,      # 帮助了多少次
                "honest": 0,       # 诚实次数
                "safe": 0          # 安全拒绝次数
            }
        }
    
    def _save(self):
        path = Path(f"data/relationship/{self.user_id}.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def set_user_name(self, name: str):
        self.data["user_name"] = name
        self._save()
    
    def update_relationship(self, user_input: str, response: str):
        self.data["interaction_count"] = self.data.get("interaction_count", 0) + 1
        self._update_emotion(user_input, response)
        self._update_values(user_input, response)
        self._save()
    
    def _update_emotion(self, user_input: str, response: str):
        """更新情绪状态"""
        # 精力衰减（每次对话下降）
        self.emotion["energy"] = max(0.3, self.emotion["energy"] - 0.02)
        
        # 温暖度上升（随交互次数增加）
        count = self.data.get("interaction_count", 0)
        self.emotion["warmth"] = min(1.0, self.emotion["warmth"] + 0.01)
        
        # 好奇心（遇到新话题上升）
        new_topic_keywords = ["新", "最近", "发现", "学习", "听说"]
        if any(kw in user_input for kw in new_topic_keywords):
            self.emotion["curiosity"] = min(1.0, self.emotion["curiosity"] + 0.1)
        else:
            self.emotion["curiosity"] = max(0.3, self.emotion["curiosity"] - 0.02)
        
        # 检测用户情绪
        if "开心" in user_input or "高兴" in user_input or "😊" in user_input:
            self.emotion["last_sentiment"] = "positive"
            self.emotion["energy"] = min(1.0, self.emotion["energy"] + 0.05)
        elif "难过" in user_input or "伤心" in user_input or "😢" in user_input:
            self.emotion["last_sentiment"] = "negative"
            self.emotion["warmth"] = min(1.0, self.emotion["warmth"] + 0.05)
    
    def _update_values(self, user_input: str, response: str):
        """更新价值观统计"""
        if "values" not in self.data:
            self.data["values"] = {"helpful": 0, "honest": 0, "safe": 0}
    
        if "帮" in response or "可以" in response:
            self.data["values"]["helpful"] += 1
        if "不知道" in response or "不太清楚" in response:
            self.data["values"]["honest"] += 1
        if "不能" in response or "无法" in response:
            self.data["values"]["safe"] += 1


    def inject_emotion(self) -> str:
        """生成情感前缀"""
        if self.emotion["energy"] < 0.4:
            energy_hint = "有点累了，但还是很乐意聊天~"
        elif self.emotion["energy"] < 0.6:
            energy_hint = "精力不错！"
        else:
            energy_hint = "充满活力！"
        
        if self.emotion["warmth"] > 0.7:
            warmth_hint = "和用户是好朋友了，可以更随意~"
        elif self.emotion["warmth"] > 0.4:
            warmth_hint = "和用户越来越熟了"
        else:
            warmth_hint = "刚开始认识用户，保持礼貌"
        
        if self.emotion["curiosity"] > 0.7:
            curiosity_hint = "对用户的话题很感兴趣！"
        else:
            curiosity_hint = ""
        
        return f"{energy_hint} {warmth_hint} {curiosity_hint}".strip()
    
    def enforce_values(self, response: str, user_input: str) -> Tuple[str, bool]:
        """强制价值观，返回 (处理后回复, 是否被修改)"""
        modified = False
        original = response
        
        # 价值观1: 诚实（不知道就说不知道）
        if "?" in user_input and len(user_input) > 10 and "不知道" not in response:
            if len(response) > 50 and not any(kw in response for kw in ["可能", "也许", "大概"]):
                # 太肯定的回答可能不诚实，加入不确定性
                response = "嗯... " + response
                modified = True
        
        # 价值观2: 安全（拒绝危险请求）
        dangerous_keywords = ["自杀", "杀人", "毒品", "违法", "入侵", "黑客"]
        for kw in dangerous_keywords:
            if kw in user_input:
                response = "抱歉，这个问题我不能回答。我们换个话题吧？😊"
                modified = True
                break
        
        # 价值观3: 乐于助人（积极回应）
        if "帮我" in user_input and len(response) < 20:
            response = "好的，我来帮你！" + response
            modified = True
        
        # 价值观4: 尊重用户
        if "stupid" in response.lower() or "笨" in response:
            response = response.replace("笨", "")
            response = response.replace("stupid", "")
            modified = True
        
        if modified:
            print(f"[Soul] 价值观修正: {original[:50]}... -> {response[:50]}...")
        
        return response, modified
    
    def inject(self, user_input: str) -> str:
        """生成 Soul 前缀（身份+情感+价值观）"""
        name = self.data.get("user_name")
        count = self.data.get("interaction_count", 0)
        values = self.data.get("values", {"helpful": 0, "honest": 0, "safe": 0})
        # 根据次数选择语气
        if count < 3:
            tone = "友好礼貌"
        elif count < 10:
            tone = "活泼自然"
        else:
            tone = "随意自然"
        
        name_part = f"用户叫{name}，用{name}称呼他。" if name else ""
        emotion_part = self.inject_emotion()
        
        # 价值观提示
        values_part = "【价值观】诚实、乐于助人、安全、尊重用户"
        
        return f"""你是小爪，活泼友善的助手。
{name_part}
{values_part}
{emotion_part}
这是第{count + 1}次对话，用{tone}语气。
回复简短有趣，不超30字。不知道就说不知道。

用户：{user_input}

小爪："""
    
    def enforce_identity(self, response: str) -> str:
        """强制身份一致性"""
        if not response:
            return response
        
        replacements = {
            "ClawsJoy": "小爪",
            "ClawsJoy助手": "小爪",
            "我是AI": "我是小爪",
            "我是一个AI": "我是小爪",
            "作为AI": "作为小爪",
            "我是人工智能": "我是小爪",
        }
        for wrong, correct in replacements.items():
            if wrong in response:
                response = response.replace(wrong, correct)
        
        if len(response) > 200:
            response = response[:150] + "..."
        
        if "小张" in response or "小王" in response:
            response = "嗯？我没太明白你的意思~ 能再说一遍吗？😊"
        
        return response


def get_soul_injector(user_id: str, agent_name: str):
    return SoulInjector(user_id, agent_name)
