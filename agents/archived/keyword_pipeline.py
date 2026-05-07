"""关键词全生命周期管理 - 完全在 Agent 层，不依赖大模型"""

import re
import json
import time
import requests
from pathlib import Path
from collections import Counter

class KeywordPipeline:
    def __init__(self, tenant_id="tenant_1"):
        self.tenant_id = tenant_id
        self.keywords_file = Path("/mnt/d/clawsjoy/data/keywords.json")
        self.pending_file = Path("/mnt/d/clawsjoy/data/keyword_pending.json")
        self.meilisearch = "http://localhost:7700"
        self._init_files()
    
    def _init_files(self):
        self.pending_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.pending_file.exists():
            with open(self.pending_file, 'w') as f:
                json.dump({"candidates": {}, "config": {"threshold": 3}}, f)
    
    # ========== 1. 采集/提取候选词 ==========
    def extract_candidates(self, text, source="user"):
        """从文本中提取候选词（纯规则，不用大模型）"""
        # 2-6 个中文字符
        candidates = re.findall(r'[\u4e00-\u9fa5]{2,6}', text)
        # 英文单词（3-10 字母）
        candidates += re.findall(r'[a-zA-Z]{3,10}', text)
        
        # 去重、去停用词
        stopwords = {'我们', '他们', '这个', '那个', '可以', '已经', '还是'}
        candidates = [c for c in set(candidates) if c not in stopwords and len(c) >= 2]
        
        # 加载已有关键词，过滤已存在的
        existing = self._get_existing_keywords()
        new_candidates = [c for c in candidates if c not in existing]
        
        # 更新暂存区
        self._update_pending(new_candidates, source)
        
        return new_candidates
    
    def _get_existing_keywords(self):
        """获取已有关键词"""
        existing = set()
        if self.keywords_file.exists():
            with open(self.keywords_file) as f:
                data = json.load(f)
                for cat in data.get("categories", {}).values():
                    for kw in cat.get("keywords", []):
                        if isinstance(kw, dict):
                            existing.add(kw.get("name", ""))
                        else:
                            existing.add(kw)
        return existing
    
    def _update_pending(self, candidates, source):
        """更新暂存区"""
        with open(self.pending_file) as f:
            pending = json.load(f)
        
        for cand in candidates:
            if cand not in pending["candidates"]:
                pending["candidates"][cand] = {
                    "count": 1,
                    "sources": [source],
                    "first_seen": time.time()
                }
            else:
                pending["candidates"][cand]["count"] += 1
                if source not in pending["candidates"][cand]["sources"]:
                    pending["candidates"][cand]["sources"].append(source)
        
        with open(self.pending_file, 'w') as f:
            json.dump(pending, f, indent=2)
    
    # ========== 2. 判断 & 入库 ==========
    def auto_learn(self, threshold=3):
        """自动学习达到阈值的关键词"""
        with open(self.pending_file) as f:
            pending = json.load(f)
        
        threshold = pending["config"].get("threshold", threshold)
        learned = []
        
        for cand, info in list(pending["candidates"].items()):
            if info["count"] >= threshold:
                # 入库
                self._add_to_keywords(cand)
                learned.append(cand)
                del pending["candidates"][cand]
        
        with open(self.pending_file, 'w') as f:
            json.dump(pending, f, indent=2)
        
        # 同步到 Meilisearch
        if learned:
            self._sync_to_meilisearch()
        
        return learned
    
    def _add_to_keywords(self, keyword, category="通用"):
        """添加关键词到主库"""
        with open(self.keywords_file) as f:
            data = json.load(f)
        
        if category not in data["categories"]:
            data["categories"][category] = {"keywords": [], "weight": 1.0}
        
        # 检查是否已存在
        existing = [k.get("name", k) for k in data["categories"][category]["keywords"]]
        if keyword not in existing:
            data["categories"][category]["keywords"].append({
                "name": keyword,
                "slug": self._to_slug(keyword)
            })
        
        with open(self.keywords_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _to_slug(self, text):
        """生成 slug"""
        slug_map = {"香港": "hongkong", "深圳": "shenzhen", "上海": "shanghai"}
        return slug_map.get(text, text.lower().replace(" ", "_"))
    
    def _sync_to_meilisearch(self):
        """同步到 Meilisearch 索引"""
        with open(self.keywords_file) as f:
            data = json.load(f)
        
        docs = []
        for cat, info in data.get("categories", {}).items():
            for kw in info.get("keywords", []):
                name = kw.get("name", kw) if isinstance(kw, dict) else kw
                docs.append({"id": name, "name": name, "category": cat})
        
        try:
            requests.post(f"{self.meilisearch}/indexes/keywords/documents", json=docs)
        except:
            pass
    
    # ========== 3. 任务编排 ==========
    def get_related_skills(self, keyword):
        """根据关键词返回相关技能"""
        skill_map = {
            "视频": "generate_video",
            "宣传片": "generate_video",
            "告警": "config_alert",
            "上传": "upload_video",
        }
        for kw, skill in skill_map.items():
            if kw in keyword:
                return skill
        return None
    
    def trigger_workflow(self, keyword, context=None):
        """触发相关任务编排"""
        skill = self.get_related_skills(keyword)
        if skill:
            print(f"🔧 关键词 '{keyword}' 触发技能: {skill}")
            # 返回技能名称，由上层调度执行
            return {"triggered": True, "skill": skill, "keyword": keyword}
        return {"triggered": False}
    
    # ========== 4. 统计和报告 ==========
    def get_stats(self):
        """获取关键词统计"""
        with open(self.keywords_file) as f:
            data = json.load(f)
        total = 0
        for cat, info in data.get("categories", {}).items():
            total += len(info.get("keywords", []))
        return {"total_keywords": total, "categories": list(data.get("categories", {}).keys())}
    
    def get_pending_stats(self):
        """获取待学习词统计"""
        with open(self.pending_file) as f:
            pending = json.load(f)
        return {"pending_count": len(pending["candidates"])}

# 集成到 TenantAgent
class TenantAgent:
    # ... 原有代码 ...
    
    def __init__(self, tenant_id="tenant_1"):
        # ... 原有代码 ...
        self.keyword_pipeline = KeywordPipeline(tenant_id)
    
    def process_user_input(self, user_input):
        """处理用户输入 - 先提取关键词"""
        # 1. 提取候选词
        new_keywords = self.keyword_pipeline.extract_candidates(user_input)
        if new_keywords:
            print(f"📝 发现新候选词: {new_keywords}")
        
        # 2. 检查是否有触发任务的强关键词
        for kw in new_keywords:
            result = self.keyword_pipeline.trigger_workflow(kw)
            if result["triggered"]:
                # 直接执行对应技能
                return self._execute_skill(result["skill"], user_input)
        
        # 3. 正常处理
        return self._chat(user_input)
    
    def _execute_skill(self, skill, user_input):
        """执行技能"""
        if skill == "generate_video":
            return self._handle_video(user_input)
        elif skill == "config_alert":
            return self._handle_alert(user_input)
        elif skill == "upload_video":
            return self._handle_upload()
        return None

if __name__ == "__main__":
    pipeline = KeywordPipeline("tenant_1")
    # 测试提取
    new = pipeline.extract_candidates("我想制作香港科技宣传片")
    print(f"提取: {new}")
    # 查看统计
    print(pipeline.get_stats())
    # 触发任务
    result = pipeline.trigger_workflow("宣传片")
    print(f"触发: {result}")
