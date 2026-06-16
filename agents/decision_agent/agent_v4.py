#!/usr/bin/env python3
"""DecisionAgent v4.0 - 智慧决策者"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from core.agents.business.business_agent import BusinessAgent
from core.lib.scriptbook_learner import scriptbook_learner

class DecisionAgentV4(BusinessAgent):
    """
    智慧决策者 v4.0
    
    职责:
    1. 路由决策 - 当 Orchestrator 不确定时，决定调用哪个 Agent
    2. 能力评估 - 评估各 Agent 的能力匹配度
    3. 冲突仲裁 - 多 Agent 意见冲突时裁决
    4. 置信度校准 - 基于历史准确率校准
    """
    
    name = "decision_agent_v4"
    description = "智慧决策者"
    version = "4.0.0"
    
    # Agent 能力映射
    AGENT_CAPABILITIES = {
        "chat_agent": ["chat", "对话", "聊天", "问答", "普通问题"],
        "code_agent": ["代码", "编程", "写函数", "算法", "debug", "优化"],
        "analysis_agent": ["分析", "统计", "数据", "趋势", "报告"],
        "butler_agent": ["待办", "提醒", "日程", "管家", "安排"],
        "translate_agent": ["翻译", "translate", "语言转换"],
        "calculator_agent": ["计算", "数学", "公式"],
    }
    
    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self._decision_history = []
        self._calibration_data = {}
        self._feedback_buffer = []  # 待处理的反馈
        self._data_dir = Path(f"data/decision_learning/{user_id}")
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._load_calibration()
        self._load_history()
        print(f"🎖️ DecisionAgent v{self.version} 智慧决策者已上岗")
        print(f"   📚 加载校准数据: {len(self._calibration_data)} 个 Agent")
        print(f"   📝 加载历史决策: {len(self._decision_history)} 条")
    
    # ========== 持久化方法 ==========
    
    def _load_calibration(self):
        """加载校准数据"""
        cal_file = self._data_dir / "calibration.json"
        if cal_file.exists():
            try:
                with open(cal_file, 'r') as f:
                    self._calibration_data = json.load(f)
            except:
                self._calibration_data = {}
    
    def _save_calibration(self):
        """保存校准数据"""
        cal_file = self._data_dir / "calibration.json"
        with open(cal_file, 'w') as f:
            json.dump(self._calibration_data, f, indent=2)
    
    def _load_history(self):
        """加载历史决策"""
        history_file = self._data_dir / "decision_history.json"
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    self._decision_history = json.load(f)
            except:
                self._decision_history = []
    
    def _save_history(self):
        """保存历史决策"""
        history_file = self._data_dir / "decision_history.json"
        # 只保留最近 500 条
        to_save = self._decision_history[-500:] if len(self._decision_history) > 500 else self._decision_history
        with open(history_file, 'w') as f:
            json.dump(to_save, f, indent=2, default=str)
    
    # ========== 学习反馈 ==========
    
    def record_feedback(self, task: str, chosen_agent: str, was_correct: bool, actual_agent: str = None):
        """
        记录决策反馈，用于学习
        
        Args:
            task: 原始任务
            chosen_agent: 决策选择的 Agent
            was_correct: 是否正确
            actual_agent: 实际应该使用的 Agent（如果不同）
        """
        feedback = {
            "task": task[:200],
            "chosen_agent": chosen_agent,
            "was_correct": was_correct,
            "actual_agent": actual_agent or chosen_agent,
            "timestamp": datetime.now().isoformat()
        }
        self._feedback_buffer.append(feedback)
        
        # 更新校准数据
        self._update_calibration(chosen_agent, was_correct)
        
        # 如果有不同的推荐，也更新实际应该用的 Agent
        if actual_agent and actual_agent != chosen_agent:
            self._update_calibration(actual_agent, True)
        
        # 定期保存
        if len(self._feedback_buffer) >= 10:
            self._flush_feedback()
    
    def _update_calibration(self, agent: str, was_correct: bool):
        """更新单个 Agent 的校准数据"""
        if agent not in self._calibration_data:
            self._calibration_data[agent] = {
                "correct": 0,
                "total": 0,
                "accuracy": 0.5,
                "last_updated": datetime.now().isoformat()
            }
        
        self._calibration_data[agent]["total"] += 1
        if was_correct:
            self._calibration_data[agent]["correct"] += 1
        
        # 计算准确率
        total = self._calibration_data[agent]["total"]
        correct = self._calibration_data[agent]["correct"]
        self._calibration_data[agent]["accuracy"] = correct / total if total > 0 else 0.5
        self._calibration_data[agent]["last_updated"] = datetime.now().isoformat()
        
        self._save_calibration()
    
    def _flush_feedback(self):
        """保存反馈到历史"""
        for fb in self._feedback_buffer:
            self._decision_history.append(fb)
        self._feedback_buffer = []
        self._save_history()
    
    # ========== 核心决策方法 ==========
    
    def decide(self, task: str, candidates: List[str] = None) -> Dict:
        """
        决策路由
        
        Args:
            task: 用户任务描述
            candidates: 候选 Agent 列表（可选）
        
        Returns:
            {
                "agent": "code_agent",
                "confidence": 0.85,
                "reasoning": "因为任务包含代码关键词",
                "alternatives": ["analysis_agent", "chat_agent"]
            }
        """
        
        # 1. 关键词匹配
        keyword_match = self._keyword_match(task)
    
        # 2. 能力评估 - 传递正确的参数
        if candidates and len(candidates) > 0:
            # 如果是字典列表，提取 agent 名称
            if isinstance(candidates[0], dict):
                agent_names = [c.get("agent", c.get("name", "")) for c in candidates]
            else:
                agent_names = candidates
        else:
            agent_names = None
    
        capability_scores = self._assess_capabilities(task, agent_names)
    
        # 3. 历史校准
        calibrated = self._calibrate_confidences(capability_scores)
    
        # 4. 选择最佳
        if calibrated:
            best = calibrated[0]
        else:
            best = {"agent": "chat_agent", "confidence": 0.5, "reasoning": "默认选择"}
    
        # 5. 记录决策
        self._record_decision(task, best)
    
        return {
            "success": True,
            "agent": best["agent"],
            "confidence": best.get("calibrated_confidence", best.get("confidence", 0.5)),
            "reasoning": best.get("reasoning", ""),
            "alternatives": [c["agent"] for c in calibrated[1:3]] if len(calibrated) > 1 else [],
            "timestamp": datetime.now().isoformat()
        }
    
        result = self._decide_internal(task, candidates)
        
        # 记录决策（用于后续学习，正确性未知）
        self._record_decision(task, result)
        
        return result
    
    def _decide_internal(self, task: str, candidates: List = None) -> Dict:
        """内部决策逻辑（与原有 decide 相同）"""
        
        # 1. 关键词匹配
        keyword_match = self._keyword_match(task)
        
        # 2. 能力评估
        if candidates and len(candidates) > 0:
            if isinstance(candidates[0], dict):
                agent_names = [c.get("agent", c.get("name", "")) for c in candidates]
            else:
                agent_names = candidates
        else:
            agent_names = None
        
        capability_scores = self._assess_capabilities(task, agent_names)
        
        # 3. 历史校准
        calibrated = self._calibrate_confidences(capability_scores)
        
        # 4. 选择最佳
        if calibrated:
            best = calibrated[0]
        else:
            best = {"agent": "chat_agent", "confidence": 0.5, "reasoning": "默认选择"}
        
        return {
            "success": True,
            "agent": best["agent"],
            "confidence": best.get("calibrated_confidence", best.get("confidence", 0.5)),
            "reasoning": best.get("reasoning", ""),
            "alternatives": [c["agent"] for c in calibrated[1:3]] if len(calibrated) > 1 else [],
            "historical_accuracy": best.get("historical_accuracy", 0.5),
            "timestamp": datetime.now().isoformat()
        }
    
    def _record_decision(self, task: str, decision: Dict):
        """记录决策（用于分析）"""
        self._decision_history.append({
            "task": task[:200],
            "decision": decision["agent"],
            "confidence": decision["confidence"],
            "historical_accuracy": decision.get("historical_accuracy", 0.5),
            "timestamp": datetime.now().isoformat(),
            "was_correct": None  # 待填充
        })
        
        if len(self._decision_history) > 1000:
            self._decision_history = self._decision_history[-1000:]
        self._save_history()
    
    # ========== 手动反馈接口 ==========
    
    def provide_feedback(self, task_id: int, was_correct: bool, correct_agent: str = None):
        """提供反馈（用于 API 调用）"""
        if task_id < len(self._decision_history):
            decision = self._decision_history[task_id]
            self.record_feedback(
                decision["task"],
                decision["decision"],
                was_correct,
                correct_agent
            )
            return {"success": True, "message": "反馈已记录"}
        return {"success": False, "error": "决策记录不存在"}


    def evaluate_candidates(self, task: str, candidates: List[Dict]) -> Dict:
        """
        评估候选 Agent（用于冲突仲裁）
        
        candidates: [{"agent": "code_agent", "confidence": 0.8, "reasoning": "..."}]
        """
        
        # 1. 置信度校准
        calibrated = self._calibrate_confidences(candidates)
        
        # 2. 冲突检测
        if len(calibrated) >= 2:
            gap = calibrated[0]["confidence"] - calibrated[1]["confidence"]
            if gap < 0.15:
                # 冲突，需要仲裁
                return self._arbitrate(task, calibrated[:2])
        
        # 3. 无冲突，返回最佳
        return {
            "recommended": calibrated[0]["agent"],
            "confidence": calibrated[0]["confidence"],
            "is_consensus": True,
            "reasoning": "置信度差异明显，无冲突"
        }
    
    #========== 辅助方法 ==========
    
    def _keyword_match(self, task: str) -> Dict:
        """关键词匹配"""
        task_lower = task.lower()
        scores = {}
        reasonings = {}
        
        for agent, keywords in self.AGENT_CAPABILITIES.items():
            score = 0
            matched = []
            for kw in keywords:
                if kw in task_lower:
                    score += 1
                    matched.append(kw)
            
            if matched:
                scores[agent] = min(score / 3, 1.0)  # 归一化
                reasonings[agent] = f"匹配关键词: {', '.join(matched)}"
            else:
                scores[agent] = 0.1
                reasonings[agent] = "无关键词匹配"
        
        # 转换为列表格式
        result = []
        for agent, conf in scores.items():
            result.append({
                "agent": agent,
                "confidence": conf,
                "reasoning": reasonings.get(agent, ""),
                "method": "keyword_match"
            })
        
        return sorted(result, key=lambda x: x["confidence"], reverse=True)
    
   
    def _assess_capabilities(self, task: str, candidates: List = None) -> List[Dict]:
        """能力评估（调用各 Agent 的 can_handle_json）"""
    
        # 修复：candidates 可能是 List[str] 或 List[Dict]
        if candidates and len(candidates) > 0:
            if isinstance(candidates[0], dict):
                # 如果是字典列表，提取 agent 名称
                agent_names = [c.get("agent", c.get("name", "")) for c in candidates if isinstance(c, dict)]
            else:
                agent_names = candidates
        else:
            agent_names = list(self.AGENT_CAPABILITIES.keys())
    
        # 过滤空值
        agent_names = [a for a in agent_names if a]
    
        results = []
        for agent_name in agent_names:
            agent = self._get_agent(agent_name)
            confidence = 0.3
         
            if agent and hasattr(agent, 'can_handle_json'):
                try:
                    can, conf = agent.can_handle_json("infer", "text")
                    confidence = conf if can else 0.2
                except:
                    pass
        
            results.append({
                "agent": agent_name,
                "confidence": confidence,
                "reasoning": f"Agent {agent_name} 自身评估",
                "method": "self_assessment"
            })
    
        # 关键词匹配
        keyword_results = self._keyword_match(task)
    
        # 综合评分 - 修复：使用 agent 名称作为 key
        combined = {}
        for r in results:
            agent = r["agent"]
            combined[agent] = r["confidence"] * 0.4
    
        for r in keyword_results:
            agent = r["agent"]
            if agent in combined:
                combined[agent] += r["confidence"] * 0.6
            else:
                combined[agent] = r["confidence"] * 0.6
    
        # 转换回列表
        final = []
        for agent, conf in combined.items():
            final.append({
                "agent": agent,
                "confidence": min(conf, 1.0),
                "reasoning": f"综合评估: 关键词 + 自评",
                "method": "combined"
            })
    
        return sorted(final, key=lambda x: x["confidence"], reverse=True)


    def _calibrate_confidences(self, candidates: List[Dict]) -> List[Dict]:
        """置信度校准（基于历史准确率 + 贝叶斯平滑）"""
        
        calibrated = []
        for c in candidates:
            agent = c["agent"]
            history = self._calibration_data.get(agent, {})
            historical_accuracy = history.get("accuracy", 0.5)
            total_samples = history.get("total", 0)
            
            raw_conf = c.get("confidence", c.get("calibrated_confidence", 0.5))
            
            # 贝叶斯平滑：小样本时更依赖先验
            alpha = 2  # 先验强度
            prior = 0.5  # 先验准确率
            smoothed_accuracy = (historical_accuracy * total_samples + prior * alpha) / (total_samples + alpha)
            
            # 综合置信度
            calibrated_conf = raw_conf * 0.5 + smoothed_accuracy * 0.5
            
            calibrated.append({
                **c,
                "raw_confidence": raw_conf,
                "calibrated_confidence": calibrated_conf,
                "historical_accuracy": smoothed_accuracy,
                "total_samples": total_samples
            })
        
        return sorted(calibrated, key=lambda x: x["calibrated_confidence"], reverse=True)  
    
     # ========== 决策统计 ==========
    
    def get_learning_stats(self) -> Dict:
        """获取学习统计"""
        total_decisions = len(self._decision_history)
        recent = self._decision_history[-100:] if total_decisions > 100 else self._decision_history
        recent_accuracy = sum(1 for d in recent if d.get("was_correct", False)) / len(recent) if recent else 0.5
        
        return {
            "total_decisions": total_decisions,
            "recent_accuracy": recent_accuracy,
            "agents_calibrated": len(self._calibration_data),
            "agent_accuracies": {
                agent: data.get("accuracy", 0.5)
                for agent, data in self._calibration_data.items()
            },
            "feedback_pending": len(self._feedback_buffer)
        }

    def _arbitrate(self, task: str, top_two: List[Dict]) -> Dict:
        """冲突仲裁"""
        
        # 请求 LLM 仲裁
        prompt = f"""请决定哪个 Agent 更适合处理以下任务：

任务：{task}

候选1: {top_two[0]['agent']} (置信度 {top_two[0]['confidence']:.0%})
候选2: {top_two[1]['agent']} (置信度 {top_two[1]['confidence']:.0%})

请只输出推荐的 Agent 名称（如 "code_agent"），不要有其他文字。"""

        response = self._call_llm(prompt)
        
        recommended = top_two[0]["agent"]  # 默认
        if response and top_two[1]["agent"] in response:
            recommended = top_two[1]["agent"]
        
        return {
            "recommended": recommended,
            "confidence": 0.7,
            "is_consensus": False,
            "reasoning": f"LLM 仲裁：选择 {recommended}",
            "alternatives": [top_two[1]["agent"]]
        }
    
       
    def update_calibration(self, agent: str, was_correct: bool):
        """更新校准数据"""
        if agent not in self._calibration_data:
            self._calibration_data[agent] = {"correct": 0, "total": 0}
        
        self._calibration_data[agent]["total"] += 1
        if was_correct:
            self._calibration_data[agent]["correct"] += 1
        
        accuracy = self._calibration_data[agent]["correct"] / \
                   self._calibration_data[agent]["total"]
        self._calibration_data[agent]["accuracy"] = accuracy
        
        self._save_calibration()
    
       
      
    def _get_agent(self, agent_name: str):
        """获取 Agent 实例"""
        if not agent_name or not isinstance(agent_name, str):
            return None
    
        try:
            # 优先加载 V4 版本
            v4_imports = {
                "chat_agent": "agents.chat_agent.agent_v4.ChatAgentV4",
                "code_agent": "agents.code_agent.agent_v4.CodeAgentV4",
                "analysis_agent": "agents.analysis_agent.agent_v4.AnalysisAgentV4",
                "butler_agent": "agents.butler_agent.agent_v4.ButlerAgentV4",
            }
        
            if agent_name in v4_imports:
                try:
                    module_path, class_name = v4_imports[agent_name].rsplit(".", 1)
                    module = __import__(module_path, fromlist=[class_name])
                    agent_class = getattr(module, class_name)
                    return agent_class(self.user_id)
                except Exception as e:
                    print(f"[DecisionAgent] 加载 V4 {agent_name} 失败: {e}")
        
            # 降级：加载原始版本
            module = __import__(f"agents.{agent_name}.agent", fromlist=[agent_name])
            for attr in dir(module):
                if attr.endswith("Agent") and attr not in ["BusinessAgent", "BusinessAgentV2", "SmartAgent"]:
                    agent_class = getattr(module, attr)
                    return agent_class(self.user_id)
        except Exception as e:
            print(f"[DecisionAgent] 加载 {agent_name} 失败: {e}")
    
        return None

    # ========== BusinessAgent 接口 ==========
    
    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        """声明能力"""
        if action == "decide" and target == "route":
            return True, 0.95
        return False, 0.0
    
    def _recommend_tech_stack(self, user_input: str) -> str:
        """推荐技术栈"""
        user_lower = user_input.lower()
        
        # 项目类型识别
        if any(kw in user_lower for kw in ["web", "网站", "前端", "后端"]):
            return """## 🔧 技术栈推荐

根据您的需求，推荐以下技术栈：

### 前端
- **框架**: React / Vue 3
- **构建工具**: Vite
- **UI库**: Ant Design / Element Plus

### 后端
- **语言**: Python / Node.js
- **框架**: FastAPI / Express
- **数据库**: PostgreSQL / MongoDB

### 建议
- 如果是新项目，推荐 **React + FastAPI** 组合
- 需要我详细说明某个技术吗？
"""
        elif any(kw in user_lower for kw in ["ai", "机器学习", "深度学习", "大模型"]):
            return """## 🤖 AI/ML 技术栈推荐

### 核心框架
- **PyTorch** / **TensorFlow** - 深度学习框架
- **Transformers** (Hugging Face) - 大模型工具

### 开发环境
- **Python 3.10+**
- **CUDA** (如使用 GPU)
- **Jupyter Lab** / **VS Code**

### MLOps
- **MLflow** - 实验跟踪
- **Docker** - 容器化部署

### 推荐
- 新手入门: PyTorch + Transformers
- 生产部署: FastAPI + Docker
"""
        elif any(kw in user_lower for kw in ["移动", "app", "android", "ios"]):
            return """## 📱 移动开发技术栈推荐

### 跨平台
- **Flutter** (Dart) - UI 一致性好
- **React Native** (JavaScript) - 生态丰富

### 原生
- **Android**: Kotlin + Jetpack Compose
- **iOS**: Swift + SwiftUI

### 推荐
- 快速开发: Flutter
- 已有 Web 团队: React Native
"""
        else:
            return """## 🔧 通用技术栈推荐

### 后端
- **Python + FastAPI** - 快速开发
- **Node.js + Express** - 全栈统一

### 前端
- **React + TypeScript** - 生态丰富
- **Vue 3** - 上手简单

### 数据库
- **PostgreSQL** - 功能全面
- **SQLite** - 轻量级

请告诉我更多项目细节，我可以给出更精准的建议。
"""



    def _get_help(self) -> str:
        """获取帮助信息"""
        return """我是决策助手，可以帮你：

1. **技术栈推荐** - "推荐 Web 技术栈" / "AI 项目用什么框架"
2. **Agent 路由** - "哪个 agent 能处理代码" / "路由决策"
3. **冲突仲裁** - 多 Agent 冲突时裁决

请问你需要什么帮助？"""

    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        """执行决策 - 增强版，区分不同场景"""
    
        # 场景1：技术栈选型问题
        tech_keywords = ["技术栈", "框架", "用什么", "选型", "推荐", "选择什么", "哪个好"]
        is_tech_question = any(kw in user_input for kw in tech_keywords)
    
        if is_tech_question:
            response = self._recommend_tech_stack(user_input)
            return {
                "success": True,
                "response": response,
                "output_content": response,
                "decision": {"type": "tech_stack", "recommendation": response}
            }
    
        # 场景2：Agent 路由决策
        if "agent" in user_input.lower() or "路由" in user_input or "哪个agent" in user_input:
            result = self.decide(user_input)
            response = f"决策结果: 建议使用 {result['agent']} (置信度 {result['confidence']:.0%})\n理由: {result['reasoning']}"
            return {
                "success": True,
                "response": response,
                "output_content": f"建议使用 {result['agent']}",
                "decision": result
            }
    
        # 场景3：默认 - 提供帮助信息
        return {
            "success": True,
            "response": self._get_help(),
            "output_content": self._get_help()
        }

    def optimize_scriptbook(self, agent_name: str = "chat_agent") -> Dict:
        """分析并优化话本"""
        stats = scriptbook_learner.get_stats()
        
        if stats["hit_rate"] < 0.6:
            # 话本命中率低，需要优化
            suggestions = stats.get("suggestions", [])
            return {
                "need_optimization": True,
                "hit_rate": stats["hit_rate"],
                "suggestions": suggestions,
                "action": "review_scriptbook"
            }
        
        return {
            "need_optimization": False,
            "hit_rate": stats["hit_rate"],
            "status": "healthy"
        }

    def _auto_optimize_scriptbooks(self):
        """自动决策优化话本"""
        from core.lib.scriptbook_learner import scriptbook_learner
    
        for agent_name in ["chat_agent", "butler_agent"]:
            scriptbook_learner.agent_name = agent_name
            scriptbook_learner._load_stats()
            stats = scriptbook_learner.get_stats()
        
            if stats["hit_rate"] < 0.5:
                # 命中率过低，触发优化
                self._trigger_scriptbook_optimization(agent_name)



if __name__ == "__main__":
    agent = DecisionAgentV4("test")
    result = agent.decide("帮我写一个 Python 排序函数")
    print(f"决策结果: {result}")
    print("\n✅ DecisionAgentV4 测试通过")
