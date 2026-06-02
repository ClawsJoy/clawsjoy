#!/usr/bin/env python3
"""导演 Agent - YouTube 频道经营总导演"""

from typing import Dict, Optional, List
from datetime import datetime, timedelta
import json

from core.agents.base.smart_agent import SmartAgent
from engine.lib.logger import engine_logger


class DirectorAgent(SmartAgent):
    """导演 Agent - 统筹 YouTube 频道经营"""
    
    name = "director_agent"
    description = "YouTube 频道导演和策划"
    version = "2.0.0"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self._load_agent_config()
        self.content_calendar = []
        self.production_status = {}
        engine_logger.get().info("🎬 导演Agent 增强版已初始化")
    
    def process(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        """处理用户请求"""
        user_lower = user_input.lower()
        
        if "策划" in user_input or "规划" in user_input:
            return self.plan_content(user_input)
        elif "脚本" in user_input:
            return self.assign_script_writer(user_input)
        elif "拍摄" in user_input:
            return self.assign_camera(user_input)
        elif "剪辑" in user_input:
            return self.assign_editor(user_input)
        elif "发布" in user_input:
            return self.assign_publisher(user_input)
        elif "日历" in user_input or "排期" in user_input:
            return self.get_calendar()
        elif "状态" in user_input:
            return self.get_production_status()
        else:
            return self.get_help()
    
    def get_help(self) -> Dict:
        """获取帮助信息"""
        return {
            "success": True,
            "response": """🎬 导演Agent - YouTube 频道经营

我可以帮你统筹整个视频制作流程：

📋 内容策划：「策划一个AI教程系列」
✍️ 脚本撰写：「生成脚本：Python入门」
🎥 拍摄安排：「安排拍摄计划」
✂️ 剪辑任务：「分配剪辑任务」
📤 发布管理：「安排发布：明天10点」
📅 内容日历：「查看内容日历」
📊 生产状态：「查看制作进度」

请告诉我你需要什么帮助！""",
            "agent": self.name,
            "user_id": self.user_id
        }
    
    def plan_content(self, prompt: str) -> Dict:
        """策划内容"""
        from core.agents.builtin.youtube_agent import youtube_agent
        
        # 提取主题
        topic = prompt.replace("策划", "").replace("规划", "").strip()
        if not topic:
            topic = "AI技术"
        
        # 生成内容创意
        ideas = youtube_agent.get_content_ideas(topic)
        
        # 创建计划
        plan = {
            "topic": topic,
            "series_name": f"{topic}系列教程",
            "episodes": len(ideas),
            "episodes_list": ideas,
            "estimated_duration": len(ideas) * 15,  # 分钟
            "planned_at": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "response": f"✅ 内容策划完成！\n📺 系列: {plan['series_name']}\n📹 集数: {plan['episodes']}集\n⏱️ 预计总时长: {plan['estimated_duration']}分钟\n\n📋 各集主题:\n" + "\n".join(f"  {i+1}. {idea}" for i, idea in enumerate(ideas)),
            "plan": plan,
            "agent": self.name,
            "user_id": self.user_id
        }
    
    def assign_script_writer(self, prompt: str) -> Dict:
        """分配脚本撰写任务"""
        from core.agents.builtin.youtube_agent import youtube_agent
        
        topic = prompt.replace("脚本", "").replace("生成", "").strip()
        if not topic:
            topic = "AI入门"
        
        # 调用 YouTube Agent 生成脚本
        result = youtube_agent.generate_script(topic)
        
        # 记录任务
        task_id = f"script_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.production_status[task_id] = {
            "type": "script",
            "topic": topic,
            "status": "completed",
            "result": result.get('script', {}),
            "created_at": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "response": f"✅ 脚本撰写任务已完成！\n📌 标题: {result.get('script', {}).get('title', 'N/A')}\n📋 大纲已生成\n\n任务ID: {task_id}",
            "task_id": task_id,
            "script": result.get('script'),
            "agent": self.name,
            "user_id": self.user_id
        }
    
    def assign_camera(self, prompt: str) -> Dict:
        """安排拍摄"""
        task_id = f"shoot_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.production_status[task_id] = {
            "type": "shooting",
            "status": "scheduled",
            "suggested_duration": 120,  # 分钟
            "created_at": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "response": "✅ 拍摄任务已安排！\n🎥 建议拍摄时长: 2小时\n📋 请准备好: 脚本、提词器、录音设备",
            "task_id": task_id,
            "agent": self.name,
            "user_id": self.user_id
        }
    
    def assign_editor(self, prompt: str) -> Dict:
        """分配剪辑任务"""
        task_id = f"edit_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.production_status[task_id] = {
            "type": "editing",
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "response": "✅ 剪辑任务已分配！\n✂️ 剪辑要点:\n  • 添加字幕\n  • 添加片头片尾\n  • 背景音乐\n  • 特效包装",
            "task_id": task_id,
            "agent": self.name,
            "user_id": self.user_id
        }
    
    def assign_publisher(self, prompt: str) -> Dict:
        """分配发布任务"""
        from core.agents.builtin.youtube_agent import youtube_agent
        
        # 解析发布时间
        publish_time = datetime.now() + timedelta(days=1)
        
        task_id = f"publish_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.production_status[task_id] = {
            "type": "publishing",
            "status": "scheduled",
            "scheduled_time": publish_time.isoformat(),
            "created_at": datetime.now().isoformat()
        }
        
        # 添加到内容日历
        self.content_calendar.append({
            "task_id": task_id,
            "type": "publish",
            "scheduled_time": publish_time.isoformat(),
            "status": "scheduled"
        })
        
        return {
            "success": True,
            "response": f"✅ 发布任务已安排！\n📅 发布时间: {publish_time.strftime('%Y-%m-%d %H:%M')}\n⏰ 请确保视频已准备好",
            "task_id": task_id,
            "agent": self.name,
            "user_id": self.user_id
        }
    
    def get_calendar(self) -> Dict:
        """获取内容日历"""
        return {
            "success": True,
            "response": f"📅 内容日历\n\n待发布: {len([c for c in self.content_calendar if c['status'] == 'scheduled'])} 项\n制作中: {len([s for s in self.production_status.values() if s['status'] != 'completed'])} 项\n\n📺 近期安排:\n" + "\n".join(f"  • {c.get('scheduled_time', 'N/A')}: {c['type']}" for c in self.content_calendar[-5:]),
            "calendar": self.content_calendar,
            "production_status": self.production_status,
            "agent": self.name,
            "user_id": self.user_id
        }
    

    
    def call_tool(self, tool_name: str, params: Dict) -> Dict:
        """调用工具"""
        from engine.tools.registry import tool_registry
        return tool_registry.execute(tool_name, params)
    
    def list_available_tools(self, category: str = None) -> List[Dict]:
        """列出可用工具"""
        from engine.tools.registry import tool_registry
        return tool_registry.list_tools(category)
    
    def execute_workflow(self, workflow_name: str, params: Dict) -> Dict:
        """执行工作流（多个工具组合）"""
        workflows = {
            "video_publish": ["transcribe", "add_subtitles", "video_composer", "youtube_uploader"],
            "audio_process": ["audio_processor", "transcribe"],
            "content_creation": ["tts", "image_recognition", "video_composer"]
        }
        
        steps = workflows.get(workflow_name, [])
        results = []
        context = params.copy()
        
        for step in steps:
            result = self.call_tool(step, context)
            results.append(result)
            if result.get('output'):
                context.update(result['output'])
        
        return {"success": True, "results": results, "steps": len(steps)}

    def get_production_status(self) -> Dict:
        """获取制作状态"""
        status_summary = {
            "script": len([s for s in self.production_status.values() if s['type'] == 'script']),
            "shooting": len([s for s in self.production_status.values() if s['type'] == 'shooting']),
            "editing": len([s for s in self.production_status.values() if s['type'] == 'editing']),
            "publishing": len([s for s in self.production_status.values() if s['type'] == 'publishing'])
        }
        
        return {
            "success": True,
            "response": f"📊 制作状态\n\n✍️ 脚本: {status_summary['script']} 项\n🎥 拍摄: {status_summary['shooting']} 项\n✂️ 剪辑: {status_summary['editing']} 项\n📤 发布: {status_summary['publishing']} 项",
            "status": status_summary,
            "details": self.production_status,
            "agent": self.name,
            "user_id": self.user_id
        }


# 全局实例
director_agent = DirectorAgent()
