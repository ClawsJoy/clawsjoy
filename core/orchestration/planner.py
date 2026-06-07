from pathlib import Path

"""任务规划器 - 将自然语言转换为任务计划"""

import re
from typing import Dict, List


class TaskPlanner:
    """任务规划器"""

    # 任务模板库
    TEMPLATES = {
        "video_production": {
            "name": "视频制作",
            "description": "制作一个{title}视频",
            "tasks": [
                {
                    "name": "understand",
                    "agent": "chat_agent",
                    "action": "understand",
                    "message": "理解需求",
                    "estimated": 5,
                },
                {
                    "name": "collect",
                    "agent": "video_agent",
                    "action": "search",
                    "message": "收集素材",
                    "estimated": 30,
                },
                {
                    "name": "script",
                    "agent": "writer_agent",
                    "action": "write",
                    "message": "生成脚本",
                    "estimated": 20,
                },
                {
                    "name": "voice",
                    "agent": "audio_agent",
                    "action": "tts",
                    "message": "制作配音",
                    "estimated": 15,
                    "optional": True,
                },
                {
                    "name": "edit",
                    "agent": "video_agent",
                    "action": "edit",
                    "message": "剪辑视频",
                    "estimated": 60,
                },
                {
                    "name": "subtitle",
                    "agent": "video_agent",
                    "action": "subtitle",
                    "message": "添加字幕",
                    "estimated": 10,
                    "optional": True,
                },
            ],
        },
        "image_generation": {
            "name": "图像生成",
            "description": "生成{title}图像",
            "tasks": [
                {
                    "name": "generate",
                    "agent": "vision_agent",
                    "action": "generate",
                    "message": "生成图像",
                    "estimated": 15,
                },
                {
                    "name": "analyze",
                    "agent": "vision_agent",
                    "action": "analyze",
                    "message": "分析图像",
                    "estimated": 10,
                    "optional": True,
                },
                {
                    "name": "optimize",
                    "agent": "vision_agent",
                    "action": "optimize",
                    "message": "优化图像",
                    "estimated": 10,
                    "optional": True,
                },
            ],
        },
        "data_analysis": {
            "name": "数据分析",
            "description": "分析{title}数据",
            "tasks": [
                {
                    "name": "collect",
                    "agent": "collector_agent",
                    "action": "collect",
                    "message": "收集数据",
                    "estimated": 20,
                },
                {
                    "name": "analyze",
                    "agent": "analysis_agent",
                    "action": "analyze",
                    "message": "分析数据",
                    "estimated": 30,
                },
                {
                    "name": "report",
                    "agent": "writer_agent",
                    "action": "write",
                    "message": "生成报告",
                    "estimated": 20,
                },
            ],
        },
    }

    def plan(self, user_input: str) -> Dict:
        """生成任务计划"""

        # 1. 识别意图
        intent = self._detect_intent(user_input)

        # 2. 提取参数
        params = self._extract_params(user_input, intent)

        # 3. 选择模板
        template = self.TEMPLATES.get(intent, self.TEMPLATES["video_production"])

        # 4. 填充模板
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
        """检测意图"""
        if "视频" in user_input and ("制作" in user_input or "剪辑" in user_input):
            return "video_production"
        elif "图片" in user_input and ("生成" in user_input or "画" in user_input):
            return "image_generation"
        elif "分析" in user_input and ("数据" in user_input or "趋势" in user_input):
            return "data_analysis"
        else:
            return "video_production"  # 默认

    def _extract_params(self, user_input: str, intent: str) -> Dict:
        """提取参数"""
        # 提取主题
        title = user_input
        keywords = ["制作", "生成", "分析", "关于", "一个"]
        for kw in keywords:
            title = title.replace(kw, "")
        title = title.strip()[:50]

        return {"title": title or "默认主题"}


class TaskExecutor:
    """任务执行器 - 不修改原有 Agent，通过标准接口调用"""

    def __init__(self):
        self.results = []
        self.checkpoints = []

    def execute(self, task: Dict, user_id: str) -> Dict:
        """执行单个任务"""
        agent_name = task.get("agent")
        action = task.get("action")
        message = task.get("message", "")

        # 通过标准接口调用 Agent
        result = self._call_agent(agent_name, action, message, user_id)

        return {
            "task": task.get("name"),
            "success": result.get("success", False),
            "result": result,
            "message": message,
        }

    def _call_agent(
        self, agent_name: str, action: str, message: str, user_id: str
    ) -> Dict:
        """调用 Agent（不修改原有代码）"""
        try:
            # 动态导入 Agent
            if agent_name == "video_agent":
                from agents.video_agent.agent import VideoAgent

                agent = VideoAgent(user_id)
                return agent.process(message)
            elif agent_name == "vision_agent":
                from agents.vision_agent.agent import VisionAgent

                agent = VisionAgent(user_id)
                return agent.process(message)
            elif agent_name == "writer_agent":
                from agents.writer_agent.agent import WriterAgent

                agent = WriterAgent(user_id)
                return agent.process(message)
            elif agent_name == "chat_agent":
                from agents.chat_agent.agent import ChatAgent

                agent = ChatAgent(user_id)
                return agent.process(message)
            else:
                from agents.executor_agent.agent import ExecutorAgent

                agent = ExecutorAgent(user_id)
                return agent.process(message)
        except Exception as e:
            return {"success": False, "error": str(e)}


class ProgressTracker:
    """进度追踪器"""

    def __init__(self, storage_dir: str = "data/orchestration"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save(self, plan_id: str, data: Dict):
        """保存进度"""
        import json

        with open(self.storage_dir / f"{plan_id}.json", "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load(self, plan_id: str) -> Dict:
        """加载进度"""
        import json

        file = self.storage_dir / f"{plan_id}.json"
        if file.exists():
            with open(file, "r") as f:
                return json.load(f)
        return {}

    def format_progress(self, completed: int, total: int) -> str:
        """格式化进度显示"""
        percent = int(completed / total * 100)
        bar_length = 20
        filled = int(bar_length * completed / total)
        bar = "█" * filled + "░" * (bar_length - filled)
        return f"[{bar}] {percent}% ({completed}/{total})"
