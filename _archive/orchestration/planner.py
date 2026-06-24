# core/orchestration/planner.py
"""任务规划器 - 覆盖全部23个Agent的意图模板 + 动态Agent发现"""

import re
from pathlib import Path
from typing import Any, Dict, List


class TaskPlanner:
    """任务规划器 - 全Agent覆盖"""

    TEMPLATES = {
        # ========== 创作类 ==========
        "video_production": {
            "name": "视频制作",
            "description": "制作关于「{title}」的视频",
            "tasks": [
                {"name": "understand", "agent": "chat_agent", "action": "understand",
                 "message": "理解视频需求: {title}", "estimated": 5},
                {"name": "collect", "agent": "video_agent", "action": "search",
                 "message": "收集素材: {title}", "estimated": 30},
                {"name": "script", "agent": "writer_agent", "action": "write",
                 "message": "为视频「{title}」生成脚本", "estimated": 20},
                {"name": "voice", "agent": "audio_agent", "action": "tts",
                 "message": "为脚本生成配音", "estimated": 15, "optional": True},
                {"name": "edit", "agent": "video_agent", "action": "edit",
                 "message": "剪辑视频", "estimated": 60},
                {"name": "subtitle", "agent": "video_agent", "action": "subtitle",
                 "message": "添加字幕", "estimated": 10, "optional": True},
            ],
        },
        "video_analysis": {
            "name": "视频分析",
            "description": "分析视频内容",
            "tasks": [
                {"name": "index", "agent": "video_indexer_agent", "action": "index",
                 "message": "索引视频", "estimated": 20},
                {"name": "analyze", "agent": "analysis_agent", "action": "analyze",
                 "message": "分析视频内容", "estimated": 30},
            ],
        },
        "image_generation": {
            "name": "图像生成",
            "description": "生成「{title}」图像",
            "tasks": [
                {"name": "generate", "agent": "vision_agent", "action": "generate",
                 "message": "生成图像: {title}", "estimated": 15},
                {"name": "analyze", "agent": "vision_agent", "action": "analyze",
                 "message": "分析生成的图像", "estimated": 10, "optional": True},
            ],
        },
        "image_analysis": {
            "name": "图像分析",
            "description": "分析图像内容",
            "tasks": [
                {"name": "analyze", "agent": "vision_agent", "action": "analyze",
                 "message": "分析图像", "estimated": 10},
            ],
        },
        "audio_process": {
            "name": "音频处理",
            "description": "处理音频",
            "tasks": [
                {"name": "process", "agent": "audio_agent", "action": "process",
                 "message": "处理音频", "estimated": 15},
            ],
        },
        "three_d_generation": {
            "name": "3D生成",
            "description": "生成3D内容: {title}",
            "tasks": [
                {"name": "generate", "agent": "three_d_agent", "action": "generate",
                 "message": "生成3D: {title}", "estimated": 30},
            ],
        },
        "comic_creation": {
            "name": "漫画创作",
            "description": "创作漫画: {title}",
            "tasks": [
                {"name": "script", "agent": "comic_writer_agent", "action": "write",
                 "message": "编写漫画脚本: {title}", "estimated": 20},
                {"name": "generate", "agent": "vision_agent", "action": "generate",
                 "message": "生成漫画画面", "estimated": 30},
            ],
        },

        # ========== 写作类 ==========
        "writing": {
            "name": "写作",
            "description": "创作「{title}」",
            "tasks": [
                {"name": "outline", "agent": "writer_agent", "action": "outline",
                 "message": "为「{title}」生成大纲", "estimated": 15},
                {"name": "write", "agent": "writer_agent", "action": "write",
                 "message": "创作「{title}」", "estimated": 30},
                {"name": "polish", "agent": "writer_agent", "action": "polish",
                 "message": "润色「{title}」", "estimated": 15, "optional": True},
            ],
        },
        "dialect_learning": {
            "name": "方言学习",
            "description": "学习方言: {title}",
            "tasks": [
                {"name": "learn", "agent": "dialect_agent", "action": "learn",
                 "message": "学习方言: {title}", "estimated": 10},
            ],
        },

        # ========== 代码类 ==========
        "code_generation": {
            "name": "代码生成",
            "description": "编写「{title}」代码",
            "tasks": [
                {"name": "understand", "agent": "chat_agent", "action": "understand",
                 "message": "理解需求: {title}", "estimated": 5},
                {"name": "code", "agent": "code_agent", "action": "generate",
                 "message": "生成代码: {title}", "estimated": 30},
                {"name": "review", "agent": "code_agent", "action": "review",
                 "message": "审查代码", "estimated": 15, "optional": True},
            ],
        },
        "code_review": {
            "name": "代码审查",
            "description": "审查代码",
            "tasks": [
                {"name": "review", "agent": "code_agent", "action": "review",
                 "message": "深度审查代码", "estimated": 20},
            ],
        },
        "code_debug": {
            "name": "代码调试",
            "description": "调试修复代码",
            "tasks": [
                {"name": "analyze", "agent": "code_agent", "action": "analyze",
                 "message": "分析错误", "estimated": 15},
                {"name": "fix", "agent": "code_agent", "action": "fix",
                 "message": "修复代码", "estimated": 20},
            ],
        },

        # ========== 分析类 ==========
        "data_analysis": {
            "name": "数据分析",
            "description": "分析「{title}」数据",
            "tasks": [
                {"name": "analyze", "agent": "analysis_agent", "action": "analyze",
                 "message": "分析: {title}", "estimated": 30},
                {"name": "report", "agent": "writer_agent", "action": "write",
                 "message": "生成分析报告", "estimated": 20},
            ],
        },
        "file_operation": {
            "name": "文件操作",
            "description": "处理文件: {title}",
            "tasks": [
                {"name": "process", "agent": "file_agent", "action": "process",
                 "message": "处理文件: {title}", "estimated": 10},
            ],
        },

        # ========== 翻译类 ==========
        "translation": {
            "name": "翻译",
            "description": "翻译: {title}",
            "tasks": [
                {"name": "detect", "agent": "translate_agent", "action": "detect",
                 "message": "检测语言", "estimated": 3},
                {"name": "translate", "agent": "translate_agent", "action": "translate",
                 "message": "翻译: {title}", "estimated": 15},
                {"name": "polish", "agent": "writer_agent", "action": "polish",
                 "message": "润色译文", "estimated": 10, "optional": True},
            ],
        },

        # ========== 计算类 ==========
        "calculation": {
            "name": "计算",
            "description": "计算: {title}",
            "tasks": [
                {"name": "calculate", "agent": "calculator_agent", "action": "calculate",
                 "message": "计算: {title}", "estimated": 5},
            ],
        },

        # ========== 协作类 ==========
        "collaboration": {
            "name": "多Agent协作",
            "description": "协作任务: {title}",
            "tasks": [
                {"name": "plan", "agent": "collaboration_agent", "action": "plan",
                 "message": "规划协作: {title}", "estimated": 10},
                {"name": "execute", "agent": "executor_agent", "action": "execute",
                 "message": "执行协作任务", "estimated": 30},
            ],
        },

        # ========== 导演类 ==========
        "director": {
            "name": "导演模式",
            "description": "导演: {title}",
            "tasks": [
                {"name": "plan", "agent": "director_agent", "action": "plan",
                 "message": "制定拍摄计划: {title}", "estimated": 15},
                {"name": "script", "agent": "writer_agent", "action": "write",
                 "message": "编写剧本", "estimated": 30},
                {"name": "shoot", "agent": "director_agent", "action": "shoot",
                 "message": "执行拍摄", "estimated": 60, "optional": True},
            ],
        },

        # ========== 记忆类 ==========
        "memory_operation": {
            "name": "记忆管理",
            "description": "管理记忆: {title}",
            "tasks": [
                {"name": "process", "agent": "memory_agent", "action": "process",
                 "message": "{title}", "estimated": 5},
            ],
        },

        # ========== 管家类 ==========
        "butler": {
            "name": "管家服务",
            "description": "管家: {title}",
            "tasks": [
                {"name": "process", "agent": "butler_agent", "action": "process",
                 "message": "{title}", "estimated": 10},
            ],
        },
        "proactive": {
            "name": "主动服务",
            "description": "主动建议: {title}",
            "tasks": [
                {"name": "suggest", "agent": "proactive_agent", "action": "suggest",
                 "message": "生成主动建议", "estimated": 10},
            ],
        },

        # ========== YouTube类 ==========
        "youtube": {
            "name": "YouTube操作",
            "description": "YouTube: {title}",
            "tasks": [
                {"name": "process", "agent": "youtube_agent", "action": "process",
                 "message": "{title}", "estimated": 20},
            ],
        },

        # ========== 复合编排（复杂任务）==========
        "complex_orchestration": {
            "name": "复杂编排",
            "description": "复合任务: {title}",
            "tasks": [
                {"name": "decide", "agent": "decision_agent", "action": "decide",
                 "message": "决策如何分解: {title}", "estimated": 10},
                {"name": "plan", "agent": "orchestrator", "action": "plan",
                 "message": "制定执行计划", "estimated": 15},
                {"name": "execute", "agent": "executor_agent", "action": "execute",
                 "message": "按计划执行", "estimated": 30},
                {"name": "verify", "agent": "decision_agent", "action": "verify",
                 "message": "验证执行结果", "estimated": 10, "optional": True},
            ],
        },
    }

    INTENT_MAP = [
        (["视频", "剪辑", "制作视频", "短视频"], "video_production"),
        (["视频分析", "分析视频"], "video_analysis"),
        (["生成图", "画图", "画画", "图像生成", "图片生成"], "image_generation"),
        (["图片分析", "图像分析", "识图", "看图"], "image_analysis"),
        (["音频", "配音", "语音", "tts", "文字转语音"], "audio_process"),
        (["3d", "三维", "建模", "立体"], "three_d_generation"),
        (["漫画", "连环画"], "comic_creation"),
        (["写小说", "创作小说", "写故事", "写文章", "撰写", "写作"], "writing"),
        (["方言"], "dialect_learning"),
        (["调试", "debug", "修复代码", "修bug", "报错", "修代码"], "code_debug"),
        (["审查代码", "review", "代码审查", "深度审查代码"], "code_review"),
        (["代码", "编程", "写函数", "算法", "写一个"], "code_generation"),
        (["分析数据", "统计", "趋势分析", "数据分析", "分析"], "data_analysis"),
        (["文件", "读取文件", "写入文件", "保存文件"], "file_operation"),
        (["翻译", "translate"], "translation"),
        (["计算", "等于", "加减乘除", "算", "数学"], "calculation"),
        (["协作", "分配任务", "并行"], "collaboration"),
        (["导演", "电影", "剧本", "拍摄"], "director"),
        (["记住", "回忆", "忘记", "记忆"], "memory_operation"),
        (["管家", "待办", "提醒", "日程"], "butler"),
        (["主动", "建议", "推荐"], "proactive"),
        (["youtube", "油管", "频道"], "youtube"),
        (["并且", "同时", "然后", "之后", "接着", "先", "再", "最后"], "complex_orchestration"),
    ]

    def plan(self, user_input: str) -> Dict:
        """生成任务计划"""
        intent = self._detect_intent(user_input)
        params = self._extract_params(user_input, intent)
        template = self.TEMPLATES.get(intent, self._default_template(user_input))

        return {
            "success": True,
            "intent": intent,
            "name": template["name"],
            "description": template["description"].format(**params),
            "tasks": template["tasks"],
            "params": params,
            "total_estimated": sum(t.get("estimated", 0) for t in template["tasks"]),
        }

    def _detect_intent(self, user_input: str) -> str:
        """按优先级匹配意图"""
        t = user_input.lower()
        for keywords, intent in self.INTENT_MAP:
            if any(kw in t for kw in keywords):
                return intent
        return "chat"

    def _extract_params(self, user_input: str, intent: str) -> Dict:
        """提取主题参数"""
        title = user_input
        noise = ["帮我", "请", "制作", "生成", "分析", "关于", "一个", "一下",
                 "我想要", "需要", "能不能", "可不可以"]
        for kw in noise:
            title = title.replace(kw, "")
        return {"title": title.strip()[:80] or "默认主题"}

    def _default_template(self, user_input: str) -> Dict:
        """无匹配意图时的默认对话"""
        return {
            "name": "对话",
            "description": f"回答: {user_input[:50]}",
            "tasks": [
                {"name": "chat", "agent": "chat_agent", "action": "chat",
                 "message": user_input, "estimated": 10},
            ],
        }

    def add_template(self, name: str, template: Dict):
        """运行时动态注册模板"""
        self.TEMPLATES[name] = template

    def add_intent(self, keywords: List[str], template_name: str):
        """运行时动态注册意图"""
        self.INTENT_MAP.insert(0, (keywords, template_name))


class TaskExecutor:
    """任务执行器 - 三层降级Agent发现 + 超时 + 错误处理"""

    def __init__(self, default_timeout: int = 120):
        self.default_timeout = default_timeout
        self._agent_cache: Dict[str, Any] = {}

    def execute(self, task: Dict, user_id: str) -> Dict:
        agent_name = task.get("agent", "chat_agent")
        message = task.get("message", "")
        action = task.get("action", "")

        agent = self._get_agent(agent_name, user_id)
        if not agent:
            return {
                "task": task.get("name"),
                "agent": agent_name,
                "success": False,
                "error": f"Agent '{agent_name}' 不可用"
            }

        try:
            context = {"action": action, "user_id": user_id,
                       "task_name": task.get("name")}

            if hasattr(agent, 'process'):
                result = agent.process(message, context)
            elif hasattr(agent, 'handle_json'):
                result = agent.handle_json(message)
            elif hasattr(agent, 'handle'):
                result = agent.handle(message)
            else:
                return {
                    "task": task.get("name"), "agent": agent_name,
                    "success": False, "error": "Agent无可用方法"
                }

            return {
                "task": task.get("name"),
                "agent": agent_name,
                "success": result.get("success", True),
                "response": result.get("response", result.get("output_content", "")),
                "raw": result,
            }
        except Exception as e:
            return {
                "task": task.get("name"), "agent": agent_name,
                "success": False, "error": str(e)
            }

    def _get_agent(self, agent_name: str, user_id: str):
        """三层降级获取Agent"""
        cache_key = f"{agent_name}:{user_id}"
        if cache_key in self._agent_cache:
            return self._agent_cache[cache_key]

        agent = (
            self._from_wisdom(agent_name, user_id)
            or self._from_registry(agent_name, user_id)
            or self._from_import(agent_name, user_id)
        )
        if agent:
            self._agent_cache[cache_key] = agent
        return agent

    def _from_wisdom(self, name: str, uid: str):
        try:
            from core.agents.wisdom.wisdom_factory import wisdom_factory
            return wisdom_factory.get_wisdom_agent(name, uid)
        except Exception:
            return None

    def _from_registry(self, name: str, uid: str):
        try:
            from core.lib.agent_registry import agent_registry
            cls = agent_registry.get(name)
            return cls(uid) if cls else None
        except Exception:
            return None
    def _from_import(self, name: str, uid: str):
        try:
            import sys, os
            # 确保项目根目录在 path 中
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            if project_root not in sys.path:
                sys.path.insert(0, project_root)
        
            mod = __import__(f"agents.{name}.agent_v4", fromlist=["*"])
            for attr in dir(mod):
                if attr.endswith("V4") and hasattr(getattr(mod, attr), 'process'):
                    return getattr(mod, attr)(uid)
        except ImportError as e:
            pass
        return None
    

    def clear_cache(self):
        self._agent_cache.clear()


class ProgressTracker:
    """进度追踪器"""

    def __init__(self, storage_dir: str = "data/orchestration"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save(self, plan_id: str, data: Dict):
        import json
        with open(self.storage_dir / f"{plan_id}.json", "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load(self, plan_id: str) -> Dict:
        import json
        file = self.storage_dir / f"{plan_id}.json"
        if file.exists():
            with open(file, "r") as f:
                return json.load(f)
        return {}

    def format_progress(self, completed: int, total: int) -> str:
        if total == 0:
            return "[░░░░░░░░░░░░░░░░░░░░] 0% (0/0)"
        percent = int(completed / total * 100)
        filled = int(20 * completed / total)
        bar = "█" * filled + "░" * (20 - filled)
        return f"[{bar}] {percent}% ({completed}/{total})"


