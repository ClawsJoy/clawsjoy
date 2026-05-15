"""自我进化引擎 - 从经验中学习并改进自身"""
import json
import hashlib
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')
from agent_core.brain_enhanced import brain

class EvolutionEngine:
    def __init__(self):
        self.evolution_log = Path("logs/evolution.log")
        self.evolution_file = Path("data/evolution.json")
        self.load_evolution()
        
    def load_evolution(self):
        if self.evolution_file.exists():
            with open(self.evolution_file, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {
                "version": 1,
                "mutations": [],
                "successful_patterns": [],
                "failed_patterns": [],
                "genome": {
                    "decision_threshold": 0.7,
                    "learning_rate": 0.3,
                    "exploration_rate": 0.2,
                    "memory_retention": 100
                }
            }
    
    def save_evolution(self):
        with open(self.evolution_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def analyze_experiences(self):
        stats = brain.get_stats()
        experiences = brain.knowledge.get('experiences', [])
        
        patterns = {"high_success": [], "low_success": [], "emerging": []}
        action_stats = defaultdict(lambda: {"success": 0, "total": 0})
        
        for exp in experiences[-100:]:
            action = exp.get('action', 'unknown')
            success = exp.get('result', {}).get('success', False)
            action_stats[action]["total"] += 1
            if success:
                action_stats[action]["success"] += 1
        
        for action, stat in action_stats.items():
            rate = stat["success"] / stat["total"] if stat["total"] > 0 else 0
            if rate > 0.8 and stat["total"] > 3:
                patterns["high_success"].append({"action": action, "success_rate": rate, "count": stat["total"]})
            elif rate < 0.3 and stat["total"] > 3:
                patterns["low_success"].append({"action": action, "success_rate": rate, "count": stat["total"]})
        
        return patterns
    
    def mutate_genome(self):
        import random
        mutations = []
        
        old_threshold = self.data["genome"]["decision_threshold"]
        new_threshold = max(0.5, min(0.9, old_threshold + random.uniform(-0.1, 0.1)))
        if new_threshold != old_threshold:
            mutations.append({"gene": "decision_threshold", "old": old_threshold, "new": new_threshold})
            self.data["genome"]["decision_threshold"] = new_threshold
        
        old_rate = self.data["genome"]["learning_rate"]
        new_rate = max(0.1, min(0.9, old_rate + random.uniform(-0.1, 0.2)))
        if new_rate != old_rate:
            mutations.append({"gene": "learning_rate", "old": old_rate, "new": new_rate})
            self.data["genome"]["learning_rate"] = new_rate
        
        if mutations:
            self.data["mutations"].append({
                "timestamp": datetime.now().isoformat(),
                "changes": mutations,
                "generation": len(self.data["mutations"]) + 1
            })
            self.save_evolution()
        
        return mutations
    
    def evolve(self):
        print("\n🧬 自我进化引擎")
        print("=" * 50)
        patterns = self.analyze_experiences()
        print(f"📊 成功模式: {len(patterns['high_success'])} 个")
        for p in patterns['high_success'][:3]:
            print(f"   ✅ {p['action']}: {p['success_rate']*100:.0f}%")
        
        if len(self.data["mutations"]) % 10 == 0:
            mutations = self.mutate_genome()
            if mutations:
                print(f"\n🧬 基因突变:")
                for m in mutations:
                    print(f"   {m['gene']}: {m['old']:.2f} -> {m['new']:.2f}")
        
        self.save_evolution()
        return {"patterns": patterns, "genome": self.data["genome"]}

if __name__ == "__main__":
    engine = EvolutionEngine()
    result = engine.evolve()
    print(f"\n📋 当前基因: {result['genome']}")
