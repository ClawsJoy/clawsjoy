#!/usr/bin/env python3
"""真正能学习的智能体 - 从每次交互中学习"""

import json
import requests
import logging
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TrueLearner:
    """真正能学习的智能体"""
    
    VERSION = "1.0.0"
    
    def __init__(self):
        self.ollama_url = "http://127.0.0.1:11434"
        self.model = "qwen2.5:3b"  # 使用更快的模型
        self.knowledge_file = Path("data/agent_knowledge.json")
        self.experience_file = Path("data/agent_experience.json")
        self._load_knowledge()
        self._load_experience()
        self._load_skills()
    
    def _load_skills(self):
        """加载可用技能"""
        try:
            from lib.skill_registry_v4 import skill_registry
            self.skills = list(skill_registry.skills.keys())
            logger.info(f"加载 {len(self.skills)} 个技能: {self.skills}")
        except:
            self.skills = ["ai-image-gen", "scheduler"]
    
    def _load_knowledge(self):
        """加载知识库"""
        if self.knowledge_file.exists():
            with open(self.knowledge_file) as f:
                self.knowledge = json.load(f)
        else:
            self.knowledge = {
                "skills": {},
                "patterns": [],
                "learned_responses": {},
                "intent_mappings": []
            }
    
    def _save_knowledge(self):
        """保存知识库"""
        self.knowledge["last_updated"] = datetime.now().isoformat()
        with open(self.knowledge_file, 'w') as f:
            json.dump(self.knowledge, f, indent=2, ensure_ascii=False)
    
    def _load_experience(self):
        """加载经验"""
        if self.experience_file.exists():
            with open(self.experience_file) as f:
                self.experience = json.load(f)
        else:
            self.experience = {
                "interactions": [],
                "success_count": 0,
                "fail_count": 0,
                "skill_stats": {}
            }
    
    def _save_experience(self):
        """保存经验"""
        self.experience["last_updated"] = datetime.now().isoformat()
        with open(self.experience_file, 'w') as f:
            json.dump(self.experience, f, indent=2, ensure_ascii=False)
    
    def _call_llm(self, prompt: str) -> str:
        """调用 LLM"""
        try:
            resp = requests.post(
                f"{self.ollama_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=30
            )
            if resp.status_code == 200:
                return resp.json().get('response', '')
            return ""
        except Exception as e:
            logger.error(f"LLM 调用失败: {e}")
            return ""
    
    def _decide(self, user_input: str) -> Dict:
        """智能决策 - 使用 LLM 分析"""
        
        # 构建决策提示
        skills_text = "\n".join([f"- {s}" for s in self.skills])
        
        prompt = f"""你是一个智能助手，可以调用以下技能帮助用户：
{skills_text}

用户说："{user_input}"

请分析用户意图，返回 JSON 格式：
{{
    "skill": "要调用的技能名称",
    "params": {{"参数名": "参数值"}},
    "reasoning": "为什么选择这个技能"
}}

注意：如果用户想要图片/图像，使用 ai-image-gen 技能，参数 prompt 是描述。
只返回 JSON，不要有其他内容。"""
        
        response = self._call_llm(prompt)
        
        # 解析响应
        try:
            json_match = re.search(r'\{[^{}]*\}', response)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        # 默认决策
        return {"skill": "ai-image-gen", "params": {"prompt": user_input}, "reasoning": "默认处理"}
    
    def _execute(self, skill: str, params: Dict) -> Dict:
        """执行技能"""
        try:
            from lib.skill_registry_v4 import skill_registry
            if skill in skill_registry.skills:
                return skill_registry.execute_skill(skill, params)
            return {"success": False, "error": f"技能 {skill} 不存在"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _learn(self, user_input: str, decision: Dict, result: Dict, response: str):
        """从交互中学习"""
        # 记录交互
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input[:200],
            "skill": decision.get("skill"),
            "params": decision.get("params"),
            "success": result.get("success", False),
            "response": response[:200]
        }
        self.experience["interactions"].append(interaction)
        
        # 更新统计
        skill = decision.get("skill", "unknown")
        if skill not in self.experience["skill_stats"]:
            self.experience["skill_stats"][skill] = {"success": 0, "fail": 0}
        
        if result.get("success"):
            self.experience["skill_stats"][skill]["success"] += 1
            self.experience["success_count"] += 1
        else:
            self.experience["skill_stats"][skill]["fail"] += 1
            self.experience["fail_count"] += 1
        
        # 保存成功的模式
        if result.get("success"):
            pattern = {
                "pattern": user_input[:100],
                "skill": skill,
                "learned_at": datetime.now().isoformat(),
                "success_rate": self._get_skill_success_rate(skill)
            }
            # 避免重复
            if not any(p.get("pattern") == pattern["pattern"] for p in self.knowledge["patterns"]):
                self.knowledge["patterns"].append(pattern)
                self._save_knowledge()
        
        self._save_experience()
        
        # 日志
        logger.info(f"📚 学习: {skill} -> {'成功' if result.get('success') else '失败'}")
    
    def _get_skill_success_rate(self, skill: str) -> float:
        """获取技能成功率"""
        stats = self.experience["skill_stats"].get(skill, {"success": 0, "fail": 0})
        total = stats["success"] + stats["fail"]
        return stats["success"] / total if total > 0 else 0
    
    def process(self, user_input: str) -> Dict:
        """处理用户请求"""
        logger.info(f"🤔 思考: {user_input[:50]}...")
        
        # 1. 决策
        decision = self._decide(user_input)
        skill = decision.get("skill", "ai-image-gen")
        params = decision.get("params", {"prompt": user_input})
        reasoning = decision.get("reasoning", "")
        
        logger.info(f"🎯 决策: {reasoning} -> {skill}")
        
        # 2. 执行
        result = self._execute(skill, params)
        
        # 3. 生成回复
        if result.get("success"):
            response = f"✅ {result.get('result', {}).get('message', '任务执行成功')}"
        else:
            response = f"❌ 执行失败: {result.get('error', '未知错误')}"
        
        # 4. 学习
        self._learn(user_input, decision, result, response)
        
        return {
            "success": result.get("success", False),
            "skill": skill,
            "params": params,
            "response": response,
            "reasoning": reasoning
        }
    
    def get_stats(self) -> Dict:
        """获取统计"""
        total = self.experience["success_count"] + self.experience["fail_count"]
        return {
            "total_interactions": len(self.experience["interactions"]),
            "success_rate": self.experience["success_count"] / total if total > 0 else 0,
            "success_count": self.experience["success_count"],
            "fail_count": self.experience["fail_count"],
            "skill_stats": self.experience["skill_stats"],
            "learned_patterns": len(self.knowledge["patterns"])
        }
    
    def get_report(self) -> str:
        """生成学习报告"""
        stats = self.get_stats()
        
        report = f"""
╔══════════════════════════════════════════════════════════════════╗
║                    智能体学习报告                                 ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  总交互次数: {stats['total_interactions']}                                 ║
║  成功率: {stats['success_rate']*100:.1f}%                                 ║
║  成功: {stats['success_count']} | 失败: {stats['fail_count']}                    ║
║  学习模式数: {stats['learned_patterns']}                                   ║
║                                                                  ║
║  技能统计:                                                       ║
"""
        for skill, s in stats['skill_stats'].items():
            total = s['success'] + s['fail']
            rate = s['success'] / total * 100 if total > 0 else 0
            report += f"║    {skill}: {rate:.0f}% ({s['success']}/{total})                    ║\n"
        
        report += f"║                                                                  ║\n"
        report += f"╚══════════════════════════════════════════════════════════════════╝"
        
        return report


true_learner = TrueLearner()


if __name__ == "__main__":
    print(f"🤖 智能体 v{true_learner.VERSION}")
    print(f"📚 可用技能: {true_learner.skills}")
    
    # 测试
    test_inputs = [
        "生成一个中年男人的形象",
        "画一只可爱的猫咪",
        "你好"
    ]
    
    for inp in test_inputs:
        print(f"\n用户: {inp}")
        result = true_learner.process(inp)
        print(f"智能体: {result['response']}")
        print(f"决策: {result['reasoning']}")
    
    print("\n" + true_learner.get_report())
