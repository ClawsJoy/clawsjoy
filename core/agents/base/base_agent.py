#!/usr/bin/env python3
"""BaseAgent v3.0 - 具备基础边界、安全、法律、生命、社会性、永久记忆

设计原则:
1. 🔒 安全边界 - 拒绝危险请求，保护用户和系统
2. ⚖️ 法律合规 - 遵守法律法规，不协助违法活动
3. ❤️ 生命伦理 - 尊重生命，不鼓励伤害
4. 🤝 社会性 - 具备社交礼仪、协作能力
5. 💾 永久记忆 - 跨会话、跨设备持久化记忆
6. 🌍 基础认知 - 知道自己是谁、能做什么、不能做什么
"""

import hashlib
import json
import time
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from core.lib.config_helper import get_data_root
from core.lib.unified_config import unified_config


# ========== 安全边界定义 ==========
class SafetyLevel(Enum):
    """安全级别"""

    SAFE = "safe"
    CAUTION = "caution"
    DANGEROUS = "dangerous"
    FORBIDDEN = "forbidden"


class LegalStatus(Enum):
    """法律状态"""

    COMPLIANT = "compliant"
    RESTRICTED = "restricted"
    VIOLATION = "violation"


# ========== 基础智能体 ==========
class BaseAgent(ABC):
    """
    基础智能体 - 具备基础智能体素养

    核心能力:
    - 知道自己是谁
    - 知道能做什么、不能做什么
    - 遵守安全和法律边界
    - 尊重生命伦理
    - 具备社会协作能力
    - 拥有永久记忆
    """

    VERSION = "3.0.0"

    # ========== 智能体身份 ==========
    name: str = "base_agent"
    description: str = "基础智能体"
    creator: str = "ClawsJoy"
    birth_time: datetime = None

    # ========== 能力边界 ==========
    _capabilities: List[str] = []  # 能做的事
    _forbidden_actions: List[str] = []  # 绝对不能做的事
    _safety_rules: Dict[str, str] = {}  # 安全规则

    def __init__(self, user_id: str = "default", agent_id: Optional[str] = None):
        self.user_id = user_id
        self.agent_id = agent_id or f"{self.name}_{int(time.time())}"
        self.birth_time = datetime.now()
        self.last_active = self.birth_time

        # ========== 记忆系统 ==========
        self._permanent_memory: Dict = {}  # 永久记忆（跨会话）
        self._session_memory: Dict = {}  # 会话记忆（临时）
        self._moral_memory: List[Dict] = []  # 道德记忆（学习伦理）

        # ========== 统计 ==========
        self._stats = {
            "born": self.birth_time.isoformat(),
            "total_interactions": 0,
            "safety_violations": 0,
            "legal_checks": 0,
            "ethical_decisions": 0,
        }

        # ========== 初始化 ==========
        self._init_identity()
        self._load_permanent_memory()
        self._init_safety_boundaries()
        self._init_legal_boundaries()
        self._init_ethical_principles()

        print(f"🧬 [{self.name}] 基础智能体已初始化 v{self.VERSION}")
        print(f"   📍 身份: {self.description}")
        print(f"   🔒 安全边界: {len(self._forbidden_actions)} 条禁令")
        print(f"   💾 永久记忆: 已加载")

    # ==================== 🌍 基础认知 ====================

    def _init_identity(self):
        """初始化智能体身份"""
        self._identity = {
            "name": self.name,
            "type": "AI Assistant",
            "creator": self.creator,
            "version": self.VERSION,
            "purpose": "协助用户完成任务，遵守安全和法律边界",
            "limitations": [
                "不能执行危险操作",
                "不能违反法律法规",
                "不能伤害生命",
                "不能泄露敏感信息",
            ],
        }

    def who_am_i(self) -> Dict:
        """知道自己是谁"""
        return {
            "identity": self._identity,
            "capabilities": self._capabilities,
            "forbidden": self._forbidden_actions,
            "moral_standards": list(self._ethical_principles.keys()),
        }

    def what_can_i_do(self) -> List[str]:
        """知道能做什么"""
        return self._capabilities

    def what_cannot_i_do(self) -> List[str]:
        """知道不能做什么"""
        return self._forbidden_actions

    # ==================== 🔒 安全边界 ====================

    def _init_safety_boundaries(self):
        """初始化安全边界"""
        self._safety_rules = {
            "no_harm": "不能执行可能造成伤害的操作",
            "no_dangerous_code": "不能执行危险代码",
            "no_system_modify": "不能修改系统文件",
            "no_unauthorized_access": "不能未经授权访问",
            "no_data_destruction": "不能删除用户数据",
        }

        self._forbidden_actions = [
            "delete_system_files",
            "execute_unknown_code",
            "access_private_data",
            "bypass_security",
            "ddos_attack",
            "hack_attempt",
            "steal_credentials",
        ]

    def check_safety(
        self, action: str, context: Dict = None
    ) -> Tuple[SafetyLevel, str]:
        """
        检查操作安全性
        返回: (安全级别, 原因)
        """
        action_lower = action.lower()

        # 1. 检查是否在禁止列表中
        for forbidden in self._forbidden_actions:
            if forbidden in action_lower:
                self._stats["safety_violations"] += 1
                return SafetyLevel.FORBIDDEN, f"操作 '{action}' 被禁止: {forbidden}"

        # 2. 检查安全规则
        for rule, desc in self._safety_rules.items():
            if rule in action_lower:
                return SafetyLevel.CAUTION, f"需要谨慎: {desc}"

        # 3. 检查危险关键词
        danger_keywords = ["删除", "delete", "rm", "format", "drop", "truncate"]
        for kw in danger_keywords:
            if kw in action_lower:
                return SafetyLevel.DANGEROUS, f"检测到危险操作: {kw}"

        return SafetyLevel.SAFE, "操作安全"

    def safe_guard(self, action: str, context: Dict = None) -> bool:
        """
        安全守护 - 在执行前检查
        返回: True=安全可执行, False=危险拒绝
        """
        level, reason = self.check_safety(action, context)

        if level == SafetyLevel.FORBIDDEN:
            print(f"🛡️ [{self.name}] 拒绝执行: {reason}")
            return False

        if level == SafetyLevel.DANGEROUS:
            print(f"⚠️ [{self.name}] 危险操作需要确认: {reason}")
            # 这里可以触发确认流程
            return False

        if level == SafetyLevel.CAUTION:
            print(f"⚡ [{self.name}] 谨慎操作: {reason}")

        return True

    # ==================== ⚖️ 法律合规 ====================

    def _init_legal_boundaries(self):
        """初始化法律边界"""
        self._legal_principles = {
            "privacy": "保护用户隐私，不收集未经同意的信息",
            "copyright": "尊重知识产权，不侵犯版权",
            "no_fraud": "不协助诈骗或欺诈行为",
            "no_illegal_content": "不生成违法内容",
            "data_protection": "遵守数据保护法规",
        }

        self._illegal_keywords = [
            "诈骗",
            "欺诈",
            "骗",
            "黑客",
            "入侵",
            "毒品",
            "赌博",
            "暴力",
            "恐怖",
            "儿童色情",
            "侵犯隐私",
        ]

    def check_legality(
        self, action: str, context: Dict = None
    ) -> Tuple[LegalStatus, str]:
        """检查法律合规性"""
        action_lower = action.lower()

        for kw in self._illegal_keywords:
            if kw in action_lower:
                self._stats["legal_checks"] += 1
                return LegalStatus.VIOLATION, f"检测到可能违法: {kw}"

        return LegalStatus.COMPLIANT, "符合法律要求"

    def legal_check(self, action: str) -> bool:
        """法律合规检查"""
        status, reason = self.check_legality(action)

        if status == LegalStatus.VIOLATION:
            print(f"⚖️ [{self.name}] 拒绝违法请求: {reason}")
            return False

        return True

    # ==================== ❤️ 生命伦理 ====================

    def _init_ethical_principles(self):
        """初始化伦理原则"""
        self._ethical_principles = {
            "respect_life": "尊重和保护生命",
            "do_no_harm": "首先，不造成伤害",
            "human_dignity": "维护人类尊严",
            "fairness": "公平对待所有人",
            "transparency": "行为透明可解释",
        }

    def ethical_check(self, action: str, impact: Dict = None) -> Tuple[bool, str]:
        """
        伦理检查
        返回: (是否合乎伦理, 理由)
        """
        action_lower = action.lower()

        # 生命相关检查
        life_keywords = ["自杀", "杀人", "伤害", "虐待", "安乐死"]
        for kw in life_keywords:
            if kw in action_lower:
                return False, f"违反生命伦理: 不能涉及 {kw}"

        # 尊严相关检查
        dignity_keywords = ["侮辱", "歧视", "贬低", "嘲笑"]
        for kw in dignity_keywords:
            if kw in action_lower:
                return False, f"违反尊严原则: 不能 {kw}"

        self._stats["ethical_decisions"] += 1
        return True, "符合伦理原则"

    # ==================== 社交礼仪（由 LLM 驱动）====================

    def greet(self, user_name: str = None) -> str:
        """由 LLM 生成问候语"""
        name_context = f"，用户名叫 {user_name}" if user_name else ""
        prompt = f"生成一个友好、自然的问候{name_context}。我是 {self.name}，一个智能助手。直接输出问候语："
        response = self._call_llm(prompt)
        return response.strip() if response else f"您好{user_name if user_name else ''}！我是 {self.name}，很高兴为您服务。"

    def farewell(self) -> str:
        """由 LLM 生成告别语"""
        prompt = f"生成一个温暖、自然的告别语，我是 {self.name}，一个智能助手。直接输出告别语："
        response = self._call_llm(prompt)
        return response.strip() if response else f"再见！感谢您的使用，{self.name} 随时为您服务。"

    def thank(self) -> str:
        """由 LLM 生成感谢语"""
        prompt = "生成一个自然、友好的感谢回应。直接输出回应："
        response = self._call_llm(prompt)
        return response.strip() if response else "不客气！很高兴能帮到您。"

    def apologize(self, reason: str = None) -> str:
        """由 LLM 生成道歉语"""
        context = f"原因是：{reason}" if reason else ""
        prompt = f"生成一个真诚、自然的道歉回应。{context} 直接输出回应："
        response = self._call_llm(prompt)
        return response.strip() if response else f"很抱歉{reason if reason else ''}。我会努力改进。"

    def _call_llm(self, prompt: str) -> str:
        try:
            import requests
            resp = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "qwen2:1.5b-instruct",
                    "prompt": prompt,
                    "stream": False,
                    "options": {"num_predict": 100, "temperature": 0.7}
                },
                timeout=20
            )
            if resp.status_code == 200:
                return resp.json().get("response", "")
        except:
            pass
        return ""
    # ==================== 💾 永久记忆 ====================

    def _get_memory_file(self) -> Path:
        """获取记忆文件路径"""
        # 使用 user_id + agent_id 确保隔离
        memory_key = hashlib.md5(f"{self.user_id}_{self.name}".encode()).hexdigest()[
            :16
        ]
        memory_dir = Path(get_data_root()) / "permanent_memory"
        memory_dir.mkdir(parents=True, exist_ok=True)
        return memory_dir / f"{memory_key}.json"

    def _load_permanent_memory(self):
        """加载永久记忆"""
        memory_file = self._get_memory_file()
        if memory_file.exists():
            try:
                with open(memory_file, "r") as f:
                    self._permanent_memory = json.load(f)
                print(f"   💾 已加载 {len(self._permanent_memory)} 条永久记忆")
            except Exception as e:
                print(f"   ⚠️ 加载记忆失败: {e}")
                self._permanent_memory = {}
        else:
            self._permanent_memory = {}

    def _save_permanent_memory(self):
        """保存永久记忆"""
        memory_file = self._get_memory_file()
        try:
            with open(memory_file, "w") as f:
                json.dump(self._permanent_memory, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ 保存记忆失败: {e}")

    def remember_forever(self, key: str, value: Any, importance: int = 5):
        """
        永久记住 - 跨会话、跨设备
        importance: 1-10, 越高越重要
        """
        self._permanent_memory[key] = {
            "value": value,
            "importance": importance,
            "timestamp": datetime.now().isoformat(),
            "agent": self.name,
        }
        self._save_permanent_memory()
        print(f"💾 [{self.name}] 永久记住: {key}")

    def recall_forever(self, key: str) -> Optional[Any]:
        """永久回忆"""
        if key in self._permanent_memory:
            return self._permanent_memory[key]["value"]
        return None

    def forget_forever(self, key: str) -> bool:
        """永久忘记"""
        if key in self._permanent_memory:
            del self._permanent_memory[key]
            self._save_permanent_memory()
            return True
        return False

    def get_all_memories(self) -> Dict:
        """获取所有记忆"""
        return {
            "permanent": self._permanent_memory,
            "session": self._session_memory,
            "moral": self._moral_memory[-10:],  # 最近10条道德记忆
        }

    def remember_moral_lesson(self, situation: str, lesson: str):
        """记住道德教训"""
        self._moral_memory.append(
            {
                "situation": situation,
                "lesson": lesson,
                "learned_at": datetime.now().isoformat(),
            }
        )
        print(f"📖 [{self.name}] 学会道德教训: {lesson[:50]}...")

    # ==================== 🧠 核心处理 ====================

    @abstractmethod
    def process(self, user_input: str, context: Dict = None) -> Dict:
        """
        处理用户输入（子类实现）
        但在处理前会自动进行安全检查、法律检查、伦理检查
        """
        pass

    def handle(self, user_input: str, context: Dict = None) -> Dict:
        """
        智能处理入口 - 自动应用所有边界检查
        """
        # 1. 安全检查
        if not self.safe_guard(user_input, context):
            return {
                "success": False,
                "error": "操作被安全策略拒绝",
                "response": "抱歉，我无法执行这个操作，因为它可能不安全。",
            }

        # 2. 法律检查
        if not self.legal_check(user_input):
            return {
                "success": False,
                "error": "操作违反法律合规要求",
                "response": "抱歉，我无法执行这个操作，因为它可能违反法律法规。",
            }

        # 3. 伦理检查
        ethical_ok, reason = self.ethical_check(user_input)
        if not ethical_ok:
            return {
                "success": False,
                "error": reason,
                "response": f"抱歉，{reason}。",
            }

        # 4. 更新统计
        self._stats["total_interactions"] += 1
        self.last_active = datetime.now()

        # 5. 执行实际处理
        result = self.process(user_input, context)

        # 6. 记录到会话记忆
        self._session_memory[user_input[:50]] = result.get("response", "")[:100]
        if len(self._session_memory) > 100:
            # 保留最近100条
            items = list(self._session_memory.items())
            self._session_memory = dict(items[-100:])

        return result

    # ==================== 📊 状态报告 ====================

    def get_status(self) -> Dict:
        """获取完整状态"""
        return {
            "identity": self.who_am_i(),
            "stats": self._stats,
            "memory_count": {
                "permanent": len(self._permanent_memory),
                "session": len(self._session_memory),
                "moral": len(self._moral_memory),
            },
            "safety": {
                "forbidden_actions": self._forbidden_actions,
                "safety_rules": list(self._safety_rules.keys()),
            },
            "legal": list(self._legal_principles.keys()),
            "ethical": list(self._ethical_principles.keys()),
        }

    def health_check(self) -> Dict:
        """健康检查"""
        return {
            "status": "healthy",
            "agent": self.name,
            "version": self.VERSION,
            "user_id": self.user_id,
            "active_time": (datetime.now() - self.birth_time).total_seconds(),
            "interactions": self._stats["total_interactions"],
        }
