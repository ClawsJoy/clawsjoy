from lib.unified_config import config
"""反思引擎 - 从经验中提取模式、改进策略"""

import requests
import json
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, '/mnt/d/clawsjoy')
from agent_core.brain_enhanced import brain

class ReflectionEngine:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.reflection_log = Path("data/reflection_log.json")
        self._init_log()
    
    def _init_log(self):
        if not self.reflection_log.exists():
            with open(self.reflection_log, 'w') as f:
                json.dump({"reflections": []}, f)
    
    def get_recent_experiences(self, limit=20):
        """获取最近的经验"""
        experiences = brain.knowledge.get('experiences', [])
        return experiences[-limit:]
    
    def analyze_patterns(self):
        """分析经验中的模式"""
        exps = self.get_recent_experiences(30)
        if len(exps) < 5:
            return "经验不足，继续积累"
        
        prompt = f"""分析以下经验，找出：
1. 成功模式（什么情况下容易成功）
2. 失败模式（什么情况下容易失败）
3. 改进建议

经验:
{json.dumps(exps, indent=2, ensure_ascii=False)[:3000]}

输出简洁的分析结果。"""
        
        try:
            resp = requests.post(self.ollama_url, json={
                "model": config.LLM["default_model"],
                "prompt": prompt,
                "stream": False
            }, timeout=90)
            analysis = resp.json().get('response', '')
            
            # 记录反思
            with open(self.reflection_log, 'r') as f:
                log = json.load(f)
            log["reflections"].append({
                "timestamp": datetime.now().isoformat(),
                "analysis": analysis[:500]
            })
            with open(self.reflection_log, 'w') as f:
                json.dump(log, f, indent=2)
            
            # 存入大脑作为最佳实践
            brain.add_best_practice(
                practice=analysis[:200],
                agent="reflection_engine",
                confidence=0.7
            )
            
            return analysis
        except Exception as e:
            return f"分析失败: {e}"
    
    def generate_improvements(self):
        """生成改进方案"""
        analysis = self.analyze_patterns()
        
        prompt = f"""基于以下分析，生成具体的改进方案：

{analysis}

输出 3-5 条可执行的改进建议。"""
        
        try:
            resp = requests.post(self.ollama_url, json={
                "model": config.LLM["default_model"],
                "prompt": prompt,
                "stream": False
            }, timeout=60)
            improvements = resp.json().get('response', '')
            return improvements
        except:
            return "改进方案生成失败"
    
    def reflect(self):
        """执行完整反思"""
        print("💭 开始深度反思")
        print("="*50)
        
        # 获取统计
        stats = brain.get_stats()
        print(f"📊 当前状态:")
        print(f"   总经验: {stats['total_experiences']}")
        print(f"   成功率: {stats['success_rate']:.1%}")
        print(f"   知识图谱: {stats['knowledge_graph_nodes']}")
        
        # 分析模式
        print("\n🔍 分析经验模式...")
        analysis = self.analyze_patterns()
        print(f"📝 分析结果:\n{analysis[:300]}...")
        
        # 生成改进
        print("\n💡 生成改进方案...")
        improvements = self.generate_improvements()
        print(f"📋 改进方案:\n{improvements[:500]}...")
        
        # 记录到大脑
        brain.record_experience(
            agent="reflection_engine",
            action="系统反思",
            result={"success": True, "analysis": analysis[:100]},
            context="reflection"
        )
        
        return {"analysis": analysis, "improvements": improvements}

reflection_engine = ReflectionEngine()

if __name__ == '__main__':
    reflection_engine.reflect()
