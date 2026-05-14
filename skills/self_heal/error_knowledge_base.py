"""错误知识库 - 模糊匹配"""
import re
from lib.memory_simple import memory

class ErrorKnowledgeBaseSkill:
    name = "error_knowledge_base"
    description = "错误修复知识库"
    version = "1.0.0"
    category = "knowledge"

    def add_knowledge(self, error_pattern, fix, confidence=0.8):
        memory.remember(
            f"error_fix|{error_pattern}|fix:{fix}|confidence:{confidence}",
            category="error_knowledge"
        )
        return {"added": True}

    def find_fix(self, error_msg):
        if not error_msg:
            return {"fix": None, "confidence": 0}
        
        all_knowledge = memory.recall("error_fix", category="error_knowledge")
        error_lower = error_msg.lower()
        
        best_match = None
        best_confidence = 0
        
        for item in all_knowledge:
            # 提取 pattern
            pattern_match = re.search(r'error_fix\|(.+?)\|', item)
            if not pattern_match:
                continue
            
            pattern = pattern_match.group(1).lower()
            
            # 模糊匹配：pattern 中的关键词是否在错误信息中
            keywords = pattern.split()
            matched = sum(1 for kw in keywords if len(kw) > 3 and kw in error_lower)
            match_ratio = matched / len(keywords) if keywords else 0
            
            if match_ratio > 0.5:  # 超过50%关键词匹配
                fix_match = re.search(r'fix:(.+?)\|', item)
                conf_match = re.search(r'confidence:([\d\.]+)', item)
                confidence = float(conf_match.group(1)) if conf_match else 0.5
                
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_match = fix_match.group(1) if fix_match else None
        
        if best_match:
            return {"fix": best_match, "confidence": best_confidence}
        
        # 兜底：关键词直接匹配
        if 'ffmpeg' in error_lower and 'not found' in error_lower:
            return {"fix": "sudo apt install ffmpeg -y", "confidence": 0.9}
        if 'address already in use' in error_lower:
            port_match = re.search(r'port (\d+)', error_lower)
            if port_match:
                return {"fix": f"fuser -k {port_match.group(1)}/tcp", "confidence": 0.9}
            return {"fix": "fuser -k PORT/tcp", "confidence": 0.8}
        if 'permission denied' in error_lower:
            return {"fix": "chmod +x <file>", "confidence": 0.85}
        if 'indentationerror' in error_lower:
            return {"fix": "检查代码缩进", "confidence": 0.6}
        if 'jsondecodeerror' in error_lower:
            return {"fix": "检查 JSON 格式", "confidence": 0.7}
        
        return {"fix": None, "confidence": 0}

    def learn_from_fix(self, error_msg, fix, success):
        confidence = 0.9 if success else 0.3
        pattern = error_msg[:50] if error_msg else "unknown"
        self.add_knowledge(pattern, fix, confidence)
        return {"learned": True}

skill = ErrorKnowledgeBaseSkill()

def init_default_knowledge():
    """初始化默认知识库（系统启动时调用）"""
    import json
    from pathlib import Path
    
    default_file = Path("data/default_error_knowledge.json")
    if not default_file.exists():
        return
    
    with open(default_file, 'r') as f:
        defaults = json.load(f)
    
    for item in defaults:
        skill.add_knowledge(item['pattern'], item['fix'], item['confidence'])
    
    print(f"✅ 已加载 {len(defaults)} 条默认知识")

# 添加学习新错误的方法
def learn_new_error(error_msg, fix, success):
    """学习新错误（供 LLM 调用）"""
    confidence = 0.9 if success else 0.3
    pattern = error_msg[:50]
    skill.add_knowledge(pattern, fix, confidence)
    return {"learned": True, "pattern": pattern}

def update_confidence(pattern, success):
    """更新置信度"""
    items = memory.recall_all(category='error_knowledge')
    for item in items:
        if pattern in item:
            # 解析当前置信度
            import re
            match = re.search(r'confidence:([\d\.]+)', item)
            if match:
                old_conf = float(match.group(1))
                # 成功+0.05，失败-0.1
                delta = 0.05 if success else -0.1
                new_conf = max(0.3, min(0.95, old_conf + delta))
                # 更新（需要重新存储）
                # 简化：记录新置信度
                memory.remember(
                    f"confidence_update|{pattern}|old:{old_conf}|new:{new_conf}",
                    category="confidence_log"
                )
                return new_conf
    return None

def update_confidence(self, pattern, success):
    """更新置信度"""
    import re
    all_items = self.memories.get('categories', {}).get('error_knowledge', [])
    
    for i, item in enumerate(all_items):
        if pattern.lower() in item.lower() or item.lower().startswith(pattern.lower()):
            # 提取当前置信度
            conf_match = re.search(r'confidence:([\d\.]+)', item)
            if conf_match:
                old_conf = float(conf_match.group(1))
                # 成功+0.05，失败-0.1
                delta = 0.05 if success else -0.1
                new_conf = max(0.3, min(0.95, old_conf + delta))
                
                # 更新（简化：记录日志）
                self.memory.remember(
                    f"confidence_update|{pattern}|old:{old_conf}|new:{new_conf}|success:{success}",
                    category="confidence_history"
                )
                return new_conf
    return None
