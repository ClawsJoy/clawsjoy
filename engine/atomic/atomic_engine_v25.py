#!/usr/bin/env python3
"""
原子引擎 v2.5 - 2.5 层 JSON 标准
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import uuid
from datetime import datetime
from typing import Dict, Union, Optional, Any

class AtomicEngineV25:
    """原子引擎 - 2.5 层 JSON 标准"""
    
    VERSION = "2.5"
    
    def __init__(self):
        print("⚛️ 原子引擎 v2.5 启动")
        self._bridge = None
        self._init_bridge()
    
    def _init_bridge(self):
        """初始化统一桥梁"""
        try:
            from core.lib.v25_unified_bridge import v25_bridge
            self._bridge = v25_bridge
        except Exception as e:
            print(f"⚠️ 统一桥梁初始化失败: {e}")
            self._bridge = None
    
    def _create_request(self, raw_input: str, action: str = "chat", 
                         user_id: str = "default", session_id: Optional[str] = None) -> Dict:
        """创建 2.5 层 JSON 请求"""
        return {
            "version": self.VERSION,
            "session_id": session_id or str(uuid.uuid4())[:8],
            "user_id": user_id,
            "thread_id": str(uuid.uuid4())[:8],
            "turn": 0,
            "raw_input": raw_input,
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "target": "text",
            "keywords": [],
            "confidence": 0.85,
            "params": {"context": {}, "options": {}},
            "output_type": "text",
            "output_content": "",
            "output_data": {},
            "status": "pending",
            "next": "continue"
        }
    
    def _create_response(self, request: Dict, output_content: str,
                          status: str = "completed", 
                          output_data: Optional[Dict] = None) -> Dict:
        """创建 2.5 层 JSON 响应 - 避免循环引用"""
        safe_output_data = {}
        if output_data and isinstance(output_data, dict):
            for key, value in output_data.items():
                if key in ['output_data', 'self', '_state', '_stats', '_cache']:
                    continue
                if isinstance(value, (str, int, float, bool, list, dict)):
                    if isinstance(value, dict):
                        safe_output_data[key] = {k: v for k, v in value.items() 
                                                 if isinstance(v, (str, int, float, bool, list, dict, type(None)))}
                    else:
                        safe_output_data[key] = value
                elif value is None:
                    safe_output_data[key] = None
        
        return {
            "version": self.VERSION,
            "session_id": request.get("session_id"),
            "user_id": request.get("user_id"),
            "thread_id": request.get("thread_id"),
            "turn": request.get("turn", 0) + 1,
            "raw_input": request.get("raw_input", ""),
            "timestamp": datetime.now().isoformat(),
            "action": request.get("action", "chat"),
            "target": request.get("target", "text"),
            "keywords": request.get("keywords", []),
            "confidence": request.get("confidence", 0.85),
            "params": request.get("params", {}),
            "output_type": request.get("output_type", "text"),
            "output_content": output_content,
            "output_data": safe_output_data,
            "status": status,
            "next": "done"
        }
    
    def _ensure_v25_response(self, request: Dict, result: Dict) -> Dict:
        """确保结果是 2.5 层 JSON"""
        if isinstance(result, dict) and "version" not in result:
            content = result.get("response", result.get("output_content", "处理完成"))
            output_data = {}
            for key in ["agent", "intent", "memories_used", "success", "result", "error"]:
                if key in result:
                    output_data[key] = result[key]
            return self._create_response(
                request,
                content,
                "completed" if result.get("success", True) else "failed",
                output_data
            )
        return result
    
    def process(self, input_data: Union[str, Dict]) -> Dict:
        """统一处理入口"""
        try:
            # 1. 解析输入
            if isinstance(input_data, str):
                request = self._create_request(raw_input=input_data)
            else:
                if "version" not in input_data:
                    request = self._create_request(
                        raw_input=input_data.get("raw_input", str(input_data)),
                        action=input_data.get("action", "chat"),
                        user_id=input_data.get("user_id", "default"),
                        session_id=input_data.get("session_id")
                    )
                    for key in ["session_id", "thread_id", "params"]:
                        if key in input_data:
                            request[key] = input_data[key]
                else:
                    request = input_data
            
            # 2. 执行路由
            action = request.get("action", "chat")
            result = self._route(request, action)
            
            # 3. 确保 2.5 层 JSON 格式
            result = self._ensure_v25_response(request, result)
            
            return result
            
        except Exception as e:
            print(f"❌ 原子引擎处理失败: {e}")
            import traceback
            traceback.print_exc()
            
            if isinstance(input_data, dict):
                return self._create_response(
                    input_data,
                    f"处理失败: {str(e)}",
                    "failed"
                )
            else:
                return {
                    "version": self.VERSION,
                    "output_content": f"处理失败: {str(e)}",
                    "status": "failed",
                    "error": str(e)
                }
    
    def _route(self, json_data: Dict, action: str) -> Dict:
        """路由到处理器"""
        handlers = {
            "chat": self._handle_chat,
            "code": self._handle_code,
            "write": self._handle_write,
            "direct": self._handle_direct,
            "memory": self._handle_memory,
            "tool": self._handle_tool,
            "skill": self._handle_skill,
            "calculate": self._handle_calculate,
            "translate": self._handle_translate,
            "analyze": self._handle_analyze,
            "file": self._handle_file,
            "orchestrate": self._handle_orchestrate,
        }
        
        handler = handlers.get(action, self._handle_chat)
        try:
            return handler(json_data)
        except Exception as e:
            print(f"⚠️ 处理器 {action} 执行失败: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e), "response": f"处理失败: {e}"}
    
    def _handle_chat(self, json_data: Dict) -> Dict:
        try:
            from core.lib.chat_engine import chat_engine
            return chat_engine.execute(
                message=json_data.get("raw_input", ""),
                user_id=json_data.get("user_id", "guest")
            )
        except Exception as e:
            return {"error": str(e), "response": f"聊天处理失败: {e}"}
    
    def _handle_code(self, json_data: Dict) -> Dict:
        try:
            from agents.code_agent.agent_v4 import CodeAgentV4
            agent = CodeAgentV4(json_data.get("user_id", "default"))
            # 构建 context，传递 session_id 用于记忆
            context = {
                "session_id": json_data.get("session_id"),
                "user_id": json_data.get("user_id", "default"),
                "raw_input": json_data.get("raw_input", "")
            }
            # 合并 params 中的 context
            if json_data.get("params") and json_data["params"].get("context"):
                context.update(json_data["params"]["context"])
            return agent.process(json_data.get("raw_input", ""), context)
        except Exception as e:
            return {"error": str(e)}
    
    def _handle_write(self, json_data: Dict) -> Dict:
        try:
            from agents.writer_agent.agent_v4 import WriterAgentV4
            agent = WriterAgentV4(json_data.get("user_id", "default"))
            context = {
                "session_id": json_data.get("session_id"),
                "user_id": json_data.get("user_id", "default"),
                "raw_input": json_data.get("raw_input", "")
            }
            if json_data.get("params") and json_data["params"].get("context"):
                context.update(json_data["params"]["context"])
            return agent.process(json_data.get("raw_input", ""), context)
        except Exception as e:
            return {"error": str(e)}
    
    def _handle_direct(self, json_data: Dict) -> Dict:
        try:
            from agents.director_agent.agent_v4 import DirectorAgentV4
            agent = DirectorAgentV4(json_data.get("user_id", "default"))
            return agent.process(json_data.get("raw_input", ""))
        except Exception as e:
            return {"error": str(e)}
    
    def _handle_memory(self, json_data: Dict) -> Dict:
        raw_input = json_data.get("raw_input", "")
        user_id = json_data.get("user_id", "default")
        
        if self._bridge:
            if "记住" in raw_input or "记忆" in raw_input:
                parts = raw_input.replace("记住", "").replace("记忆", "").strip().split(":", 1)
                if len(parts) == 2:
                    key, value = parts[0].strip(), parts[1].strip()
                    return self._bridge.remember(user_id, key, value, json_data.get("session_id"))
            elif "回忆" in raw_input or "想起" in raw_input:
                key = raw_input.replace("回忆", "").replace("想起", "").strip()
                return self._bridge.recall(user_id, key, json_data.get("session_id"))
        
        return {"error": "请使用'记住 key: value'或'回忆 key'"}
    
    def _handle_tool(self, json_data: Dict) -> Dict:
        params = json_data.get("params", {})
        tool_name = params.get("tool", "")
        tool_params = params.get("params", {})
        user_id = json_data.get("user_id", "default")
        
        if self._bridge:
            return self._bridge.execute_tool(user_id, tool_name, tool_params, json_data.get("session_id"))
        else:
            return {"error": "工具系统不可用"}
    
    def _handle_skill(self, json_data: Dict) -> Dict:
        """处理技能请求"""
        params = json_data.get("params", {})
        skill_action = params.get("skill", "list")
        user_id = json_data.get("user_id", "default")
        raw_input = json_data.get("raw_input", "")
        
        try:
            from core.lib.skill_recommender import skill_recommender
            
            if skill_action == "list":
                # 列出所有可用技能
                return skill_recommender.get_available_skills()
            elif skill_action == "install":
                # 安装技能
                skill_name = params.get("skill_name", "")
                return skill_recommender.install(skill_name, user_id)
            elif skill_action == "uninstall":
                # 卸载技能
                skill_name = params.get("skill_name", "")
                return skill_recommender.uninstall(skill_name)
            else:
                # 推荐技能
                return skill_recommender.recommend(raw_input, user_id)
        except Exception as e:
            return {"error": str(e), "response": f"技能处理失败: {e}", "success": False}
    
    def _handle_calculate(self, json_data: Dict) -> Dict:
        try:
            from agents.calculator_agent.agent_v4 import CalculatorAgentV4
            agent = CalculatorAgentV4(json_data.get("user_id", "default"))
            return agent.process(json_data.get("raw_input", ""))
        except Exception as e:
            return {"error": str(e)}
    
    def _handle_translate(self, json_data: Dict) -> Dict:
        try:
            from agents.translate_agent.agent_v4 import TranslateAgentV4
            agent = TranslateAgentV4(json_data.get("user_id", "default"))
            context = {
                "session_id": json_data.get("session_id"),
                "user_id": json_data.get("user_id", "default"),
                "raw_input": json_data.get("raw_input", "")
            }
            if json_data.get("params") and json_data["params"].get("context"):
                context.update(json_data["params"]["context"])
            return agent.process(json_data.get("raw_input", ""), context)
        except Exception as e:
            return {"error": str(e)}
    
    def _handle_analyze(self, json_data: Dict) -> Dict:
        try:
            from agents.analysis_agent.agent_v4 import AnalysisAgentV4
            agent = AnalysisAgentV4(json_data.get("user_id", "default"))
            return agent.process(json_data.get("raw_input", ""))
        except Exception as e:
            return {"error": str(e)}
    
    def _handle_file(self, json_data: Dict) -> Dict:
        try:
            from agents.file_agent.agent_v4 import FileAgentV4
            agent = FileAgentV4(json_data.get("user_id", "default"))
            return agent.process(json_data.get("raw_input", ""))
        except Exception as e:
            return {"error": str(e)}
    
    def _handle_orchestrate(self, json_data: Dict) -> Dict:
        try:
            from agents.orchestrator.agent_v4 import OrchestratorV4
            agent = OrchestratorV4(json_data.get("user_id", "default"))
            result = agent.process(json_data.get("raw_input", ""))
            # 确保返回字典
            if not isinstance(result, dict):
                return {"response": str(result), "success": True}
            return result
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"error": str(e), "response": f"编排失败: {e}", "success": False}
    
    def get_capabilities(self) -> Dict:
        return {
            "version": self.VERSION,
            "name": "atomic_engine_v25",
            "handlers": ["chat", "code", "write", "direct", "memory", "tool", 
                        "skill", "calculate", "translate", "analyze", "file", "orchestrate"]
        }

# 全局实例
atomic_engine = AtomicEngineV25()
