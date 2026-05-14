from lib.unified_config import config
#!/usr/bin/env python3
"""自主工具链学习系统 - Agent 自己决定用哪些工具、怎么组合"""

import json
import subprocess
import requests
from datetime import datetime
from pathlib import Path
import sys
import random

sys.path.insert(0, '/mnt/d/clawsjoy')

class AutonomousLearner:
    def __init__(self):
        self.chain_file = Path("data/tool_chains.json")
        self.performance_file = Path("data/chain_performance.json")
        self.ollama_url = "http://localhost:11434/api/generate"
        self.chains = self._load_chains()
        self.performance = self._load_performance()
    
    def _load_chains(self):
        if self.chain_file.exists():
            with open(self.chain_file, 'r') as f:
                return json.load(f)
        return {"chains": [], "total": 0}
    
    def _load_performance(self):
        if self.performance_file.exists():
            with open(self.performance_file, 'r') as f:
                return json.load(f)
        return {"history": [], "best_chain": None, "success_rate": 0}
    
    def _save_chains(self):
        with open(self.chain_file, 'w') as f:
            json.dump(self.chains, f, indent=2)
    
    def _save_performance(self):
        with open(self.performance_file, 'w') as f:
            json.dump(self.performance, f, indent=2)
    
    def discover_available_tools(self):
        """发现所有可用工具"""
        from skills.skill_interface import skill_registry
        return skill_registry.get_skill_names()
    
    def llm_generate_chain(self, goal, available_tools):
        """LLM 生成工具链"""
        prompt = f"""目标: {goal}

可用工具: {available_tools}

请设计一个工具链（多个工具按顺序组合）来完成目标。
输出 JSON 格式:
{{
    "chain_name": "链名称",
    "description": "链描述",
    "steps": [
        {{"tool": "工具名", "params": {{}}, "expected_output": "预期输出"}}
    ],
    "expected_score": 0-100
}}

如果使用多个工具，请说明数据如何传递。
只输出 JSON。"""
        
        try:
            resp = requests.post(self.ollama_url, json={
                "model": config.LLM["default_model"],
                "prompt": prompt,
                "stream": False
            }, timeout=90)
            response = resp.json().get('response', '')
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1:
                return json.loads(response[start:end])
        except Exception as e:
            print(f"链生成失败: {e}")
        return None
    
    def execute_chain(self, chain, test_input=None):
        """执行工具链并评分"""
        if not test_input:
            test_input = {"test": True}
        
        context = {}
        results = []
        total_score = 0
        
        print(f"🔗 执行链: {chain.get('chain_name', 'unknown')}")
        
        for i, step in enumerate(chain.get('steps', []), 1):
            tool_name = step.get('tool')
            params = step.get('params', {})
            
            # 合并上下文
            if context:
                params['context'] = context
            
            print(f"  步骤 {i}: {tool_name}")
            
            # 调用工具
            try:
                from skills.skill_interface import skill_registry
                skill = skill_registry.get(tool_name)
                if skill:
                    result = skill.execute(params)
                    success = result.get('success', False)
                    score = 10 if success else 0
                    
                    # 提取输出作为上下文
                    if success:
                        if 'images' in result:
                            context['images'] = result['images']
                        if 'script' in result:
                            context['script'] = result['script']
                        if 'video_file' in result:
                            context['video_file'] = result['video_file']
                    
                    results.append({
                        "step": i,
                        "tool": tool_name,
                        "success": success,
                        "score": score,
                        "output": str(result)[:200]
                    })
                    total_score += score
                else:
                    results.append({"step": i, "tool": tool_name, "success": False, "score": 0})
                    total_score += 0
            except Exception as e:
                results.append({"step": i, "tool": tool_name, "success": False, "error": str(e), "score": 0})
        
        chain_result = {
            "chain_name": chain.get('chain_name'),
            "total_score": total_score,
            "max_possible": len(chain.get('steps', [])) * 10,
            "success_rate": total_score / max(1, len(chain.get('steps', [])) * 10),
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
        return chain_result
    
    def compare_and_evolve(self, results):
        """比较结果，进化最佳链"""
        if not results:
            return
        
        best = max(results, key=lambda x: x.get('total_score', 0))
        
        if not self.performance['best_chain'] or best['total_score'] > self.performance['best_chain'].get('total_score', 0):
            self.performance['best_chain'] = best
            print(f"🏆 发现新最佳链! 得分: {best['total_score']}")
        
        # 计算整体成功率
        total_score = sum(r.get('total_score', 0) for r in results)
        max_score = sum(r.get('max_possible', 100) for r in results)
        self.performance['success_rate'] = total_score / max(1, max_score)
        
        self.performance['history'].append({
            "timestamp": datetime.now().isoformat(),
            "best_score": best.get('total_score', 0),
            "success_rate": self.performance['success_rate']
        })
        
        # 保留最近100条历史
        self.performance['history'] = self.performance['history'][-100:]
        self._save_performance()
    
    def mutate_chain(self, chain, available_tools):
        """变异现有链，尝试改进"""
        prompt = f"""基于以下工具链，生成一个改进版本。

原链: {json.dumps(chain, ensure_ascii=False)}
可用工具: {available_tools}

请输出改进后的 JSON（格式相同）。可以：
- 替换低效工具
- 增加新步骤
- 删除无用步骤
- 调整参数

只输出 JSON。"""
        
        try:
            resp = requests.post(self.ollama_url, json={
                "model": config.LLM["default_model"],
                "prompt": prompt,
                "stream": False
            }, timeout=90)
            response = resp.json().get('response', '')
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1:
                return json.loads(response[start:end])
        except:
            pass
        return None
    
    def autonomous_evolution(self, goal, iterations=5):
        """自主进化：自己设计链 → 执行 → 评分 → 变异 → 重复"""
        print(f"🧬 自主进化开始")
        print(f"目标: {goal}")
        print(f"迭代次数: {iterations}")
        print("="*50)
        
        available_tools = self.discover_available_tools()
        print(f"🔧 可用工具数: {len(available_tools)}")
        
        # 1. 生成初始链
        print(f"\n📋 生成初始链...")
        initial_chain = self.llm_generate_chain(goal, available_tools)
        if not initial_chain:
            print("❌ 无法生成初始链")
            return None
        
        self.chains['chains'].append(initial_chain)
        self.chains['total'] += 1
        self._save_chains()
        
        results = []
        current_chain = initial_chain
        
        for i in range(iterations):
            print(f"\n🔄 迭代 {i+1}/{iterations}")
            
            # 执行当前链
            result = self.execute_chain(current_chain)
            results.append(result)
            print(f"   得分: {result['total_score']}/{result['max_possible']}")
            print(f"   成功率: {result['success_rate']:.1%}")
            
            # 变异生成新链
            print(f"   🧬 变异中...")
            new_chain = self.mutate_chain(current_chain, available_tools)
            if new_chain:
                current_chain = new_chain
                self.chains['chains'].append(current_chain)
                self.chains['total'] += 1
                self._save_chains()
                print(f"   ✅ 生成变异链")
            else:
                print(f"   ⚠️ 变异失败，继续使用当前链")
        
        # 比较所有结果
        self.compare_and_evolve(results)
        
        print("\n" + "="*50)
        print(f"📊 进化完成!")
        print(f"   最佳得分: {self.performance['best_chain']['total_score'] if self.performance['best_chain'] else 0}")
        print(f"   整体成功率: {self.performance['success_rate']:.1%}")
        
        return self.performance['best_chain']

# 创建自主运行实例
learner = AutonomousLearner()

if __name__ == '__main__':
    # 让 Agent 自己决定学什么
    goals = [
        "制作香港宣传视频",
        "采集并分析AI新闻", 
        "生成并发布YouTube视频"
    ]
    
    for goal in goals:
        print("\n" + "="*60)
        best_chain = learner.autonomous_evolution(goal, iterations=3)
        if best_chain:
            print(f"\n🏆 最佳链: {best_chain.get('chain_name')}")
        print("\n" + "="*60)
