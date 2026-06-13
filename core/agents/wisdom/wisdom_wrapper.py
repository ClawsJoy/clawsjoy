"""智慧包装器 - 为现有 Agent 添加智慧能力，零侵入"""

from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from collections import defaultdict
import json
import hashlib
import time


@dataclass
class Experience:
    """经验记录"""
    input: str
    output: str
    success: bool
    confidence: float
    response_time: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    reflection: Optional[str] = None


@dataclass
class CapabilityProfile:
    """能力画像"""
    action: str
    target: str
    success_count: int = 0
    total_count: int = 0
    avg_confidence: float = 0.5
    avg_response_time: float = 0
    last_used: Optional[str] = None
    
    @property
    def success_rate(self) -> float:
        return self.success_count / self.total_count if self.total_count > 0 else 0.5
    
    @property
    def confidence_score(self) -> float:
        """综合置信度 = 成功率 * 平均置信度"""
        return self.success_rate * self.avg_confidence

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "action": self.action,
            "target": self.target,
            "success_count": self.success_count,
            "total_count": self.total_count,
            "success_rate": self.success_rate,
            "avg_confidence": self.avg_confidence,
            "avg_response_time": self.avg_response_time,
            "confidence_score": self.confidence_score,
            "last_used": self.last_used
        }


class WisdomWrapper:
    """
    智慧包装器 - 为 Agent 添加智慧能力
    
    使用方式:
        agent = ChatAgent(user_id="alice")
        wisdom_agent = WisdomWrapper(agent)
        result = wisdom_agent.process("帮我分析这段代码")
    """
    
    def __init__(self, agent, config: Dict = None):
        self._agent = agent
        self._config = config or self._default_config()
        
        # ========== 智慧核心 ==========
        self._experiences: List[Experience] = []           # 经验库
        self._capability_profiles: Dict[str, CapabilityProfile] = {}  # 能力画像
        self._reflection_queue: List[Experience] = []      # 待反思的经验
        self._evolution_strategies: List[Dict] = []        # 进化策略
        
        # ========== 元认知 ==========
        self._uncertainty_threshold = 0.6
        self._self_awareness = {
            "name": getattr(agent, 'name', 'unknown'),
            "version": getattr(agent, 'version', '1.0'),
            "capabilities": [],
            "limitations": [],
            "confidence_baseline": 0.7
        }
        
        # ========== 联邦 ==========
        self._federated_knowledge: Dict = {}
        self._peer_agents: List[str] = []
        
        # ========== 统计 ==========
        self._stats = {
            "total_processed": 0,
            "success_count": 0,
            "delegated_count": 0,
            "self_reflections": 0,
            "evolutions": 0
        }
        
        # 初始化
        self._init_capability_profiles()
        self._load_experiences()
        
        print(f"🧠 智慧包装器已激活: {self._self_awareness['name']}")
    
    def _default_config(self) -> Dict:
        return {
            "learning_enabled": True,
            "reflection_batch_size": 10,
            "evolution_interval": 100,
            "federated_enabled": True,
            "max_experiences": 1000,
            "uncertainty_threshold": 0.6
        }
    def __getattr__(self, name):
        """透传未定义的方法到原始 Agent"""
        if hasattr(self._agent, name):
            return getattr(self._agent, name)
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    # ==================== 核心入口 ====================
    
    def process(self, user_input: str, context: Dict = None) -> Dict:
        """智慧处理入口 - 带元认知和执行链"""
        self._current_input = user_input  # 保存当前输入
        start_time = time.time()
        self._stats["total_processed"] += 1
        
        # ========== 1. 感知层 ==========
        perception = self._perceive(user_input)
        
        # ========== 2. 认知层 ==========
        cognition = self._cognize(user_input, perception)
        
        # ========== 3. 决策层 ==========
        decision = self._decide(user_input, cognition)
        
        # ========== 4. 执行层 ==========
        result = self._execute(decision, context)
        
        # ========== 5. 学习层 ==========
        experience = self._record_experience(
            user_input, result, start_time, cognition
        )
        
        # ========== 6. 智慧层 ==========
        if self._config["learning_enabled"]:
            self._reflect_and_learn(experience)
        
        # 包装结果
        return self._wrap_result(result, cognition, experience)
    
    # ==================== 感知层 ====================
    
    def _perceive(self, user_input: str) -> Dict:
        """感知层 - 理解输入、识别情感、检测不确定性"""
        
        perception = {
            "raw_input": user_input,
            "length": len(user_input),
            "timestamp": datetime.now().isoformat()
        }
        
        # 情感识别
        if hasattr(self._agent, 'recognize_emotion'):
            emotion, confidence = self._agent.recognize_emotion(user_input)
            perception["emotion"] = emotion.value if hasattr(emotion, 'value') else str(emotion)
            perception["emotion_confidence"] = confidence
        
        # 意图初步识别
        perception["intent"] = self._infer_intent(user_input)
        
        # 不确定性检测
        perception["uncertainty"] = self._detect_uncertainty(user_input)
        
        # 复杂度评估
        perception["complexity"] = self._assess_complexity(user_input)
        
        return perception
    
    def _detect_uncertainty(self, text: str) -> float:
        """检测输入的不确定性"""
        uncertainty_keywords = [
            "可能", "也许", "大概", "不确定", "不知道", 
            "maybe", "perhaps", "uncertain", "not sure"
        ]
        count = sum(1 for kw in uncertainty_keywords if kw in text.lower())
        return min(count / 5, 1.0)
    
    def _assess_complexity(self, text: str) -> str:
        """评估任务复杂度"""
        if len(text) > 100:
            return "high"
        if any(kw in text for kw in ["并且", "然后", "同时", "and", "then"]):
            return "medium"
        return "low"
    
    def _infer_intent(self, text: str) -> Dict:
        """推断意图（简化版）"""
        # 如果有意图解析器，使用它
        try:
            from core.lib.unified_intent_parser import unified_parser
            result = unified_parser.parse(text)
            return {
                "action": result.get("action", "chat"),
                "target": result.get("target", "text"),
                "confidence": result.get("confidence", 0.5)
            }
        except:
            # 简单规则
            if any(kw in text for kw in ["代码", "编程", "写"]):
                return {"action": "generate", "target": "code", "confidence": 0.7}
            if any(kw in text for kw in ["翻译", "translate"]):
                return {"action": "translate", "target": "text", "confidence": 0.8}
            if any(kw in text for kw in ["分析", "分析一下"]):
                return {"action": "analyze", "target": "data", "confidence": 0.7}
            return {"action": "chat", "target": "text", "confidence": 0.9}
    
    # ==================== 认知层 ====================
    
    def _cognize(self, user_input: str, perception: Dict) -> Dict:
        """认知层 - 自我评估、能力匹配、置信度计算"""
        
        intent = perception["intent"]
        action = intent["action"]
        target = intent["target"]
        
        # 获取该能力的历史画像
        cap_key = f"{action}_{target}"
        profile = self._capability_profiles.get(cap_key)
        
        if profile:
            # 基于历史数据评估
            capability_score = profile.confidence_score
            success_rate = profile.success_rate
        else:
            # 试探性评估
            capability_score = 0.5
            success_rate = 0.5
        
        # 询问 Agent 自身
        agent_can = self._ask_agent_capability(action, target)
        
        # 综合置信度
        confidence = (
            capability_score * 0.4 +
            success_rate * 0.3 +
            agent_can * 0.3
        )
        
        # 不确定性修正
        uncertainty = perception["uncertainty"]
        if uncertainty > 0.5:
            confidence *= (1 - uncertainty)
        
        # 自我认知
        self_awareness = {
            "can_handle": confidence > self._config["uncertainty_threshold"],
            "confidence": confidence,
            "capability_score": capability_score,
            "success_rate": success_rate,
            "uncertainty_aware": uncertainty > 0.3
        }
        
        # 如果置信度低，考虑委托
        if not self_awareness["can_handle"]:
            self_awareness["should_delegate"] = True
            self_awareness["delegation_candidates"] = self._find_delegation_candidates(action, target)
        
        return {
            "intent": intent,
            "self_awareness": self_awareness,
            "profile": profile.to_dict() if profile else None
        }
    
    def _ask_agent_capability(self, action: str, target: str) -> float:
        """询问 Agent 自身能力"""
        # 优先使用新的 JSON 能力接口
        if hasattr(self._agent, 'can_handle_json'):
            can, conf = self._agent.can_handle_json(action, target)
            return conf if can else 0.0
        
        # 使用旧的 can_handle
        if hasattr(self._agent, 'can_handle'):
            result = self._agent.can_handle(f"{action} {target}")
            if isinstance(result, dict):
                return result.get("confidence", 0.5) if result.get("can", False) else 0.0
            elif isinstance(result, bool):
                return 0.8 if result else 0.0
        
        # 默认试探
        return 0.5
    
    def _find_delegation_candidates(self, action: str, target: str) -> List[str]:
        """找到可委托的候选 Agent"""
        candidates = []
        
        # 从联邦知识中查找
        for agent_name, capabilities in self._federated_knowledge.items():
            caps = capabilities.get("capabilities", [])
            if f"{action}_{target}" in caps or action in caps:
                candidates.append(agent_name)
        
        # 从配置中获取
        try:
            from core.lib.agent_registry import agent_registry
            all_agents = agent_registry.list_agents()
            for agent in all_agents:
                if agent != self._self_awareness["name"]:
                    candidates.append(agent)
        except:
            pass
        
        return candidates[:3]
    
    # ==================== 决策层 ====================
    
    def _decide(self, user_input: str, cognition: Dict) -> Dict:
        """决策层 - 联邦投票、共识机制"""
        
        decision = {
            "strategy": "direct",
            "target_agent": None,
            "reasoning": []
        }
        
        self_awareness = cognition["self_awareness"]
        
        # 情况1: 自己可以处理
        if self_awareness["can_handle"]:
            decision["strategy"] = "direct"
            decision["reasoning"].append(f"自信度 {self_awareness['confidence']:.0%}，自己处理")
            return decision
        
        # 情况2: 需要委托
        if self_awareness.get("should_delegate"):
            # 联邦投票
            consensus = self._federated_voting(cognition)
            
            if consensus["has_consensus"]:
                decision["strategy"] = "delegate"
                decision["target_agent"] = consensus["winner"]
                decision["consensus_confidence"] = consensus["confidence"]
                decision["reasoning"] = consensus["reasoning"]
                return decision
        
        # 情况3: 降级 - 仍然自己处理但降低期望
        decision["strategy"] = "degraded"
        decision["reasoning"].append("无法委托，降级处理")
        
        return decision
    
    def _federated_voting(self, cognition: Dict) -> Dict:
        """联邦投票 - 多 Agent 共识"""
        
        intent = cognition["intent"]
        candidates = cognition["self_awareness"].get("delegation_candidates", [])
        
        if not candidates:
            return {"has_consensus": False}
        
        # 收集各 Agent 意见
        opinions = []
        for candidate in candidates:
            opinion = self._query_agent_opinion(candidate, intent["action"], intent["target"])
            if opinion:
                opinions.append(opinion)
        
        if not opinions:
            return {"has_consensus": False}
        
        # 加权投票
        total_weight = sum(o["confidence"] for o in opinions)
        best = max(opinions, key=lambda o: o["confidence"])
        
        # 计算共识强度
        consensus_strength = best["confidence"] / total_weight if total_weight > 0 else 0
        
        return {
            "has_consensus": consensus_strength > 0.5,
            "winner": best["agent"],
            "confidence": best["confidence"],
            "reasoning": [f"联邦投票: {best['agent']} 获得最高置信度 {best['confidence']:.0%}"]
        }
    
    def _query_agent_opinion(self, agent_name: str, action: str, target: str) -> Optional[Dict]:
        """查询其他 Agent 的意见"""
        try:
            # 通过联邦知识获取
            if agent_name in self._federated_knowledge:
                caps = self._federated_knowledge[agent_name]
                cap_key = f"{action}_{target}"
                if cap_key in caps.get("scores", {}):
                    return {
                        "agent": agent_name,
                        "confidence": caps["scores"][cap_key],
                        "can_handle": caps["scores"][cap_key] > 0.5
                    }
        except:
            pass
        return None
    
    # ==================== 执行层 ====================
    
    def _execute(self, decision: Dict, context: Dict = None) -> Dict:
        """执行层 - 根据决策执行"""
        
        if decision["strategy"] == "delegate":
            return self._execute_delegation(decision)
        else:
            return self._execute_direct(decision, context)
    
    def _execute_direct(self, decision: Dict, context: Dict = None) -> Dict:
        """直接执行"""
    
        # 获取用户输入 - 优先使用保存的当前输入
        user_input = getattr(self, '_current_input', '')
    
        # 如果保存的输入为空，尝试从 context 获取
        if not user_input and context:
            if "json_input" in context:
                json_input = context["json_input"]
                user_input = json_input.get("raw_input", json_input.get("message", ""))
            elif "user_input" in context:
                user_input = context["user_input"]
    
        # 如果还是为空，尝试从决策中获取
        if not user_input and decision.get("user_input"):
            user_input = decision.get("user_input")
    
        print(f"[DEBUG] _execute_direct - user_input: {user_input[:50] if user_input else 'EMPTY'}")
    
        # 调用原有 Agent
        if hasattr(self._agent, 'handle_json'):
            # 如果有 JSON 能力
            if context and "json_input" in context:
                return self._agent.handle_json(context["json_input"])
            return self._agent.process(user_input)
        elif hasattr(self._agent, 'process'):
            return self._agent.process(user_input)
        elif hasattr(self._agent, 'handle'):
            return self._agent.handle(user_input)
    
        return {"success": False, "response": "Agent 不可用", "output_content": "Agent 不可用"}

    def _execute_delegation(self, decision: Dict) -> Dict:
        """委托执行"""
        self._stats["delegated_count"] += 1
        
        target = decision["target_agent"]
        
        # 记录委托
        return {
            "success": True,
            "delegated_to": target,
            "response": f"我将把这个问题转交给 {target} 处理，TA 在这方面更有经验。",
            "output_content": f"转交给 {target} 处理",
            "delegation_info": decision
        }
    
    # ==================== 学习层 ====================
    
    def _record_experience(self, user_input: str, result: Dict, 
                           start_time: float, cognition: Dict) -> Experience:
        """记录经验"""
        
        response_time = (time.time() - start_time) * 1000
        # 安全处理 result 可能为 None 的情况
        if result is None:
            result = {}
        
        success = result.get("success", False)
        
        # 安全获取输出内容
        output_content = result.get("response") or result.get("output_content") or ""


        # 获取实际使用的能力
        intent = cognition.get("intent", {})
        cap_key = f"{intent.get('action', 'chat')}_{intent.get('target', 'text')}"
        
        # 更新能力画像
        if cap_key not in self._capability_profiles:
            self._capability_profiles[cap_key] = CapabilityProfile(
                action=intent.get('action', 'chat'),
                target=intent.get('target', 'text')
            )
        
        profile = self._capability_profiles[cap_key]
        profile.total_count += 1
        if success:
            profile.success_count += 1
              
        # 更新平均置信度
        self_awareness = cognition.get("self_awareness", {})
        current_conf = self_awareness.get("confidence", 0.5)
        profile.avg_confidence = (profile.avg_confidence * (profile.total_count - 1) + current_conf) / profile.total_count
        profile.avg_response_time = (profile.avg_response_time * (profile.total_count - 1) + response_time) / profile.total_count
        profile.last_used = datetime.now().isoformat()



        # 创建经验
        experience = Experience(
            input=user_input[:500],
            output=result.get("response", result.get("output_content", ""))[:500],
            success=success,
            confidence=current_conf,
            response_time=response_time
        )
        
        self._experiences.append(experience)
        
        # 限制经验库大小
        if len(self._experiences) > self._config["max_experiences"]:
            self._experiences = self._experiences[-self._config["max_experiences"]:]
        
        # 加入反思队列
        if not success or current_conf < 0.5:
            self._reflection_queue.append(experience)
        
        # 更新统计
        if success:
            self._stats["success_count"] += 1
        
        return experience
    
    def _reflect_and_learn(self, experience: Experience):
        """反思并学习"""
        
        # 批量反思
        if len(self._reflection_queue) >= self._config["reflection_batch_size"]:
            self._deep_reflection()
        
        # 定期进化
        if self._stats["total_processed"] % self._config["evolution_interval"] == 0:
            self._evolve()
    
    def _deep_reflection(self):
        """深度反思 - 分析失败模式"""
        
        self._stats["self_reflections"] += 1
        
        failures = [exp for exp in self._reflection_queue if not exp.success]
        if not failures:
            self._reflection_queue = []
            return
        
        # 分析失败原因
        failure_analysis = {
            "total_failures": len(failures),
            "common_patterns": self._analyze_failure_patterns(failures),
            "suggestions": []
        }
        
        # 生成改进建议
        for pattern in failure_analysis["common_patterns"]:
            suggestion = self._generate_improvement_suggestion(pattern)
            if suggestion:
                failure_analysis["suggestions"].append(suggestion)
        
        # 应用改进
        self._apply_improvements(failure_analysis["suggestions"])
        
        # 清空队列
        self._reflection_queue = []
    
    def _analyze_failure_patterns(self, failures: List[Experience]) -> List[Dict]:
        """分析失败模式"""
        patterns = []
        
        # 按置信度分组
        low_confidence = [f for f in failures if f.confidence < 0.4]
        if low_confidence:
            patterns.append({
                "type": "low_confidence",
                "count": len(low_confidence),
                "avg_confidence": sum(f.confidence for f in low_confidence) / len(low_confidence)
            })
        
        # 按响应时间分组
        slow_response = [f for f in failures if f.response_time > 5000]
        if slow_response:
            patterns.append({
                "type": "timeout",
                "count": len(slow_response),
                "avg_response_time": sum(f.response_time for f in slow_response) / len(slow_response)
            })
        
        return patterns
    
    def _generate_improvement_suggestion(self, pattern: Dict) -> Optional[Dict]:
        """生成改进建议"""
        if pattern["type"] == "low_confidence":
            return {
                "action": "adjust_threshold",
                "new_threshold": max(0.3, self._config["uncertainty_threshold"] - 0.1),
                "reason": f"置信度阈值过高，导致 {pattern['count']} 次失败"
            }
        elif pattern["type"] == "timeout":
            return {
                "action": "delegate_before_timeout",
                "timeout_ms": 3000,
                "reason": f"响应超时 {pattern['avg_response_time']:.0f}ms"
            }
        return None
    
    def _apply_improvements(self, suggestions: List[Dict]):
        """应用改进建议"""
        for suggestion in suggestions:
            if suggestion["action"] == "adjust_threshold":
                self._config["uncertainty_threshold"] = suggestion["new_threshold"]
                print(f"📊 智慧进化: 调整置信度阈值至 {suggestion['new_threshold']}")
    
    def _evolve(self):
        """进化 - 优化策略"""
        
        self._stats["evolutions"] += 1
        
        # 计算整体表现
        recent_experiences = self._experiences[-100:]
        if not recent_experiences:
            return
        
        success_rate = sum(1 for e in recent_experiences if e.success) / len(recent_experiences)
        
        # 进化策略
        evolutions = []
        
        # 如果成功率低于 70%，降低阈值
        if success_rate < 0.7:
            old = self._config["uncertainty_threshold"]
            self._config["uncertainty_threshold"] = max(0.3, old - 0.05)
            evolutions.append(f"成功率 {success_rate:.0%} < 70%，阈值 {old:.1f} → {self._config['uncertainty_threshold']:.1f}")
        
        # 如果委托次数过多，优化能力评估
        delegation_rate = self._stats["delegated_count"] / max(self._stats["total_processed"], 1)
        if delegation_rate > 0.5:
            evolutions.append(f"委托率 {delegation_rate:.0%} 过高，增强能力评估")
        
        if evolutions:
            print(f"🧬 智慧进化 [#{self._stats['evolutions']}]: {', '.join(evolutions)}")
    
    # ==================== 联邦知识共享 ====================
    
    def share_capability(self, target_agent: str) -> bool:
        """分享能力画像给其他 Agent"""
        if not self._config["federated_enabled"]:
            return False
        
        knowledge = {
            "agent": self._self_awareness["name"],
            "capabilities": {
                key: {
                    "success_rate": p.success_rate,
                    "avg_confidence": p.avg_confidence,
                    "total_tasks": p.total_count
                }
                for key, p in self._capability_profiles.items()
            },
            "version": self._self_awareness["version"],
            "shared_at": datetime.now().isoformat()
        }
        
        # 通过消息总线分享
        try:
            from core.lib.agent_communication import agent_communication
            agent_communication.send(target_agent, "federated.knowledge", knowledge)
        except:
            pass
        
        return True
    
    def receive_knowledge(self, from_agent: str, knowledge: Dict):
        """接收联邦知识"""
        self._federated_knowledge[from_agent] = knowledge
        print(f"🤝 从 {from_agent} 收到联邦知识，涵盖 {len(knowledge.get('capabilities', {}))} 项能力")
    
    # ==================== 元认知接口 ====================
    
    def get_self_awareness(self) -> Dict:
        """获取自我认知"""
        return {
            "identity": self._self_awareness,
            "capability_profiles": {
                key: {
                    "success_rate": p.success_rate,
                    "avg_confidence": p.avg_confidence,
                    "total_tasks": p.total_count,
                    "avg_response_time": p.avg_response_time
                }
                for key, p in self._capability_profiles.items()
            },
            "stats": self._stats,
            "config": self._config,
            "experiences_count": len(self._experiences)
        }
    
    def explain_decision(self, user_input: str) -> Dict:
        """解释决策过程"""
        perception = self._perceive(user_input)
        cognition = self._cognize(user_input, perception)
        decision = self._decide(user_input, cognition)
        
        return {
            "input": user_input,
            "perception": perception,
            "cognition": cognition,
            "decision": decision,
            "explanation": self._generate_explanation(perception, cognition, decision)
        }
    
    def _generate_explanation(self, perception: Dict, cognition: Dict, decision: Dict) -> str:
        """生成可读的解释"""
        lines = [
            f"📝 输入: {perception['raw_input'][:50]}...",
            f"🎯 意图: {cognition['intent']['action']}/{cognition['intent']['target']} (置信度 {cognition['intent']['confidence']:.0%})",
            f"🧠 自我评估: 自信度 {cognition['self_awareness']['confidence']:.0%}",
            f"⚡ 决策: {decision['strategy']}"
        ]
        
        if decision.get("reasoning"):
            lines.append(f"💭 推理: {' → '.join(decision['reasoning'])}")
        
        return "\n".join(lines)
    
    # ==================== 辅助方法 ====================
    
    def _init_capability_profiles(self):
        """初始化能力画像"""
        # 从 Agent 获取能力
        if hasattr(self._agent, '_get_capability_list'):
            caps = self._agent._get_capability_list()
            for cap in caps:
                if isinstance(cap, tuple) and len(cap) == 2:
                    key = f"{cap[0]}_{cap[1]}"
                    self._capability_profiles[key] = CapabilityProfile(action=cap[0], target=cap[1])
                elif isinstance(cap, str):
                    self._capability_profiles[cap] = CapabilityProfile(action=cap, target="text")
    
    def _load_experiences(self):
        """加载历史经验"""
        # 可以从持久化存储加载
        pass
    
    def _wrap_result(self, result: Dict, cognition: Dict, experience: Experience) -> Dict:
        """包装结果，添加元认知信息"""
        
        # 如果已经是标准化格式，添加智慧层信息
        if "version" in result:
            result["meta_cognition"] = {
                "confidence": cognition["self_awareness"]["confidence"],
                "strategy": result.get("strategy", "direct"),
                "reflection_applied": experience.reflection is not None
            }
            if "output_data" not in result:
                result["output_data"] = {}
            result["output_data"]["wisdom"] = {
                "self_confidence": cognition["self_awareness"]["confidence"],
                "experience_count": len(self._experiences)
            }
            return result
        
        # 旧格式转换
        return {
            "success": result.get("success", False),
            "response": result.get("response", result.get("output_content", "")),
            "output_content": result.get("output_content", result.get("response", "")),
            "output_data": {
                **result.get("output_data", {}),
                "wisdom": {
                    "self_confidence": cognition["self_awareness"]["confidence"],
                    "experience_count": len(self._experiences)
                }
            },
            "agent": getattr(self._agent, 'name', 'unknown'),
            "user_id": getattr(self._agent, 'user_id', 'default'),
            "meta_cognition": {
                "confidence": cognition["self_awareness"]["confidence"],
                "strategy": "wisdom_wrapped"
            }
        }


    def handle_json(self, standard_json: dict) -> dict:
        """处理标准化 JSON 输入"""
        # 提取原始输入
        raw_input = standard_json.get("raw_input", "")
        if not raw_input:
            raw_input = standard_json.get("message", "")
        
        # 如果有 message 字段，使用它
        if not raw_input and "message" in standard_json:
            raw_input = standard_json["message"]
        
        # 如果还是没有，从 keywords 构建
        if not raw_input:
            keywords = standard_json.get("keywords", [])
            raw_input = " ".join(keywords) if keywords else "chat"
        
        # 调用 process 方法
        return self.process(raw_input)
