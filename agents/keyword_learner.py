#!/usr/bin/env python3
"""关键词自动学习引擎"""

import re
import json
import time
from pathlib import Path

class KeywordLearner:
    def __init__(self):
        self.keywords_file = Path("/mnt/d/clawsjoy/data/keywords.json")
        self.pending_file = Path("/mnt/d/clawsjoy/data/keyword_pending.json")
        self._init_files()
    
    def _init_files(self):
        self.pending_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.pending_file.exists():
            with open(self.pending_file, 'w') as f:
                json.dump({"candidates": {}, "config": {"threshold": 2}}, f)
    
    def extract_candidates(self, text, source="user"):
        """提取候选词"""
        candidates = set(re.findall(r'[\u4e00-\u9fa5]{2,4}', text))
        candidates.update(re.findall(r'[a-zA-Z]{3,8}', text))
        
        stopwords = {'我们', '他们', '这个', '那个', '可以', '已经', '还是', '一个', '没有', '不是',
                     '制作', '上传', '生成', '宣传', '视频', '分钟', '配置', '钉钉', '告警', '你好',
                     '香港', '上海', '深圳', '北京'}
        
        candidates = [c for c in candidates if c not in stopwords and len(c) >= 2]
        existing = self._get_existing_keywords()
        new_candidates = [c for c in candidates if c not in existing]
        
        self._update_pending(new_candidates, source)
        return new_candidates
    
    def _get_existing_keywords(self):
        existing = set()
        if self.keywords_file.exists():
            with open(self.keywords_file) as f:
                data = json.load(f)
            for cat, info in data.get("categories", {}).items():
                for kw in info.get("keywords", []):
                    name = kw.get("name", kw) if isinstance(kw, dict) else kw
                    existing.add(name)
        return existing
    
    def _update_pending(self, candidates, source):
        with open(self.pending_file) as f:
            pending = json.load(f)
        
        now = time.time()
        for cand in candidates:
            if cand not in pending["candidates"]:
                pending["candidates"][cand] = {"count": 1, "sources": [source], "first_seen": now, "last_seen": now}
            else:
                pending["candidates"][cand]["count"] += 1
                pending["candidates"][cand]["last_seen"] = now
        
        with open(self.pending_file, 'w') as f:
            json.dump(pending, f, indent=2)
    
    def auto_learn(self, default_category="通用"):
        with open(self.pending_file) as f:
            pending = json.load(f)
        
        threshold = pending["config"].get("threshold", 2)
        learned = []
        
        for cand, info in list(pending["candidates"].items()):
            if info["count"] >= threshold:
                category = self._predict_category(cand)
                self._add_to_keywords(cand, category)
                learned.append({"keyword": cand, "category": category, "count": info["count"]})
                del pending["candidates"][cand]
        
        if learned:
            with open(self.pending_file, 'w') as f:
                json.dump(pending, f, indent=2)
            print(f"📚 学习了 {len(learned)} 个新关键词")
        
        return learned
    
    def _predict_category(self, keyword):
        maps = {
            "移民": ["优才", "高才", "人才", "签证", "永居", "身份", "落户"],
            "教育": ["留学", "大学", "申请", "学位", "硕士", "博士"],
            "科技": ["人工智能", "AI", "芯片", "科技", "机器", "学习", "算法"],
            "生活": ["租房", "美食", "交通", "购物"],
            "工作": ["求职", "招聘", "工作", "职位", "面试"]
        }
        for cat, words in maps.items():
            for w in words:
                if w in keyword or keyword in w:
                    return cat
        return "通用"
    
    def _add_to_keywords(self, keyword, category):
        with open(self.keywords_file) as f:
            data = json.load(f)
        
        if category not in data["categories"]:
            data["categories"][category] = {"keywords": [], "weight": 1.0}
        
        exists = False
        for kw in data["categories"][category]["keywords"]:
            name = kw.get("name", kw) if isinstance(kw, dict) else kw
            if name == keyword:
                exists = True
                break
        
        if not exists:
            data["categories"][category]["keywords"].append({"name": keyword, "slug": keyword.lower()})
            with open(self.keywords_file, 'w') as f:
                json.dump(data, f, indent=2)
    
    def get_stats(self):
        """获取统计"""
        with open(self.keywords_file) as f:
            data = json.load(f)
        total = 0
        for cat, info in data.get("categories", {}).items():
            total += len(info.get("keywords", []))
        
        with open(self.pending_file) as f:
            pending = json.load(f)
        
        return {
            "total_keywords": total,
            "pending_count": len(pending.get("candidates", {})),
            "by_category": {cat: len(info.get("keywords", [])) for cat, info in data.get("categories", {}).items()}
        }

if __name__ == "__main__":
    learner = KeywordLearner()
    print("统计:", learner.get_stats())

    def self_learn_from_logs(self):
        """从日志中自我学习新词"""
        import re
        from pathlib import Path
        
        log_file = Path("/mnt/d/clawsjoy/logs/chat-api-out.log")
        if not log_file.exists():
            return []
        
        with open(log_file) as f:
            logs = f.read()
        
        # 提取用户输入中的潜在新词
        patterns = [
            r'📥 处理: (.*?)\.\.\.',
            r'用户: (.*?)$',
        ]
        
        new_candidates = []
        for pattern in patterns:
            matches = re.findall(pattern, logs, re.MULTILINE)
            for match in matches[:50]:  # 每次最多学习50条
                # 提取2-4字中文词
                words = re.findall(r'[\u4e00-\u9fa5]{2,4}', match)
                for w in words:
                    if w not in self._get_existing_keywords() and len(w) >= 2:
                        new_candidates.append(w)
        
        # 去重并更新暂存区
        new_candidates = list(set(new_candidates))
        if new_candidates:
            self._update_pending(new_candidates, "self_learn")
            print(f"📚 自我学习: 发现 {len(new_candidates)} 个新候选词")
        
        return new_candidates
    
    def auto_learn_loop(self, interval_minutes=30):
        """自动学习循环"""
        import time
        while True:
            print(f"🔄 关键词学习器自动学习 (间隔{interval_minutes}分钟)")
            self.self_learn_from_logs()
            learned = self.auto_learn()
            if learned:
                print(f"✅ 新学习 {len(learned)} 个关键词")
            time.sleep(interval_minutes * 60)

    def self_learn_from_logs(self):
        """从日志中自我学习新词"""
        import re
        from pathlib import Path
        
        log_file = Path("/mnt/d/clawsjoy/logs/chat-api-out.log")
        if not log_file.exists():
            return []
        
        with open(log_file) as f:
            logs = f.read()
        
        # 提取用户输入中的潜在新词
        patterns = [
            r'📥 处理: (.*?)\.\.\.',
            r'用户: (.*?)$',
        ]
        
        new_candidates = []
        for pattern in patterns:
            matches = re.findall(pattern, logs, re.MULTILINE)
            for match in matches[:50]:  # 每次最多学习50条
                # 提取2-4字中文词
                words = re.findall(r'[\u4e00-\u9fa5]{2,4}', match)
                for w in words:
                    if w not in self._get_existing_keywords() and len(w) >= 2:
                        new_candidates.append(w)
        
        # 去重并更新暂存区
        new_candidates = list(set(new_candidates))
        if new_candidates:
            self._update_pending(new_candidates, "self_learn")
            print(f"📚 自我学习: 发现 {len(new_candidates)} 个新候选词")
        
        return new_candidates
    
    def auto_learn_loop(self, interval_minutes=30):
        """自动学习循环"""
        import time
        while True:
            print(f"🔄 关键词学习器自动学习 (间隔{interval_minutes}分钟)")
            self.self_learn_from_logs()
            learned = self.auto_learn()
            if learned:
                print(f"✅ 新学习 {len(learned)} 个关键词")
            time.sleep(interval_minutes * 60)

    def self_learn_from_logs(self):
        """从日志中自我学习新词"""
        import re
        from pathlib import Path
        
        log_file = Path("/mnt/d/clawsjoy/logs/chat-api-out.log")
        if not log_file.exists():
            return []
        
        with open(log_file) as f:
            logs = f.read()
        
        # 提取用户输入中的潜在新词
        patterns = [
            r'📥 处理: (.*?)\.\.\.',
            r'用户: (.*?)$',
        ]
        
        new_candidates = []
        for pattern in patterns:
            matches = re.findall(pattern, logs, re.MULTILINE)
            for match in matches[:50]:  # 每次最多学习50条
                # 提取2-4字中文词
                words = re.findall(r'[\u4e00-\u9fa5]{2,4}', match)
                for w in words:
                    if w not in self._get_existing_keywords() and len(w) >= 2:
                        new_candidates.append(w)
        
        # 去重并更新暂存区
        new_candidates = list(set(new_candidates))
        if new_candidates:
            self._update_pending(new_candidates, "self_learn")
            print(f"📚 自我学习: 发现 {len(new_candidates)} 个新候选词")
        
        return new_candidates
    
    def auto_learn_loop(self, interval_minutes=30):
        """自动学习循环"""
        import time
        while True:
            print(f"🔄 关键词学习器自动学习 (间隔{interval_minutes}分钟)")
            self.self_learn_from_logs()
            learned = self.auto_learn()
            if learned:
                print(f"✅ 新学习 {len(learned)} 个关键词")
            time.sleep(interval_minutes * 60)

    def self_learn_from_logs(self):
        """从日志中自我学习新词"""
        import re
        from pathlib import Path
        
        log_file = Path("/mnt/d/clawsjoy/logs/chat-api-out.log")
        if not log_file.exists():
            return []
        
        try:
            with open(log_file) as f:
                logs = f.read()[-5000:]  # 读取最近5000字符
        except:
            return []
        
        # 提取用户输入中的潜在新词
        patterns = [
            r'📥 处理: (.*?)\.\.\.',
            r'用户: (.*?)$',
        ]
        
        new_candidates = []
        for pattern in patterns:
            matches = re.findall(pattern, logs, re.MULTILINE)
            for match in matches[:50]:
                words = re.findall(r'[\u4e00-\u9fa5]{2,4}', match)
                for w in words:
                    existing = self._get_existing_keywords()
                    if w not in existing and len(w) >= 2:
                        new_candidates.append(w)
        
        new_candidates = list(set(new_candidates))
        if new_candidates:
            self._update_pending(new_candidates, "self_learn")
            print(f"📚 自我学习: 发现 {len(new_candidates)} 个新候选词")
        
        return new_candidates
