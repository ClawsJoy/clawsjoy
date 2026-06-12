"""统一意图解析器 - 标准化 JSON v1.0"""

import yaml
import json
import re
import requests
import uuid
from datetime import datetime
from pathlib import Path
from string import Template
from typing import Dict, Any, Optional


class UnifiedIntentParser:
    """统一意图解析器 - 输出标准化 JSON"""
    
    # 标准枚举值
    ACTIONS = ["play", "search", "generate", "schedule", "translate", "calculate", "chat"]
    TARGETS = ["media", "code", "image", "info", "task", "text", "number"]
    OUTPUT_TYPES = ["text", "image", "video", "link", "code"]
    STATUSES = ["pending", "processing", "completed", "failed"]
    NEXT_ACTIONS = ["continue", "done", "wait"]
    
    def __init__(self, spec_path="config/prompt/unified_spec.yaml"):
        self.spec = self._load_spec(spec_path)
        self.llm_url = "http://localhost:5012/chat"
        self.prompt_template = self._load_prompt_template()
    
    def _load_spec(self, path: str) -> Dict:
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    
    def _load_prompt_template(self) -> Template:
        prompt_path = Path("prompts/unified_intent.prompt")
        with open(prompt_path, 'r') as f:
            return Template(f.read())
    
    def _generate_session_id(self) -> str:
        return str(uuid.uuid4())[:8]
    
    def parse(self, raw_input: str, user_id: str = "default", 
              thread_id: str = None, session_id: str = None) -> Dict[str, Any]:
        """解析用户输入，输出标准化 JSON"""
        
        # 生成会话标识
        if not session_id:
            session_id = self._generate_session_id()
        if not thread_id:
            thread_id = self._generate_session_id()
        
        # 构建提示词
        prompt = self.prompt_template.substitute(raw_prompt=raw_input)
        
        action = "chat"
        target = "text"
        keywords = []
        confidence = 0.5
        
        try:
            resp = requests.post(
                self.llm_url,
                json={"message": prompt},
                timeout=30
            )
            if resp.status_code == 200:
                result = resp.json()
                response = result.get("response", "")
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    intent_data = json.loads(json_match.group())
                    action = intent_data.get("action", "chat")
                    target = intent_data.get("target", "text")
                    keywords = intent_data.get("keywords", [])
                    confidence = intent_data.get("confidence", 0.8)
                    
                    # 验证枚举值
                    if action not in self.ACTIONS:
                        action = "chat"
                    if target not in self.TARGETS:
                        target = "text"
        except Exception as e:
            print(f"意图解析失败: {e}")
        
        # 构建标准化 JSON
        return {
            "version": "1.0",
            "session_id": session_id,
            "user_id": user_id,
            "thread_id": thread_id,
            "turn": 0,
            "raw_input": raw_input,
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "target": target,
            "keywords": keywords,
            "confidence": confidence,
            "params": {},
            "output_type": "text",
            "output_content": "",
            "output_data": {},
            "status": "pending",
            "next": "continue"
        }
    
    def get_agent_name(self, standardized_json: Dict) -> str:
        """根据标准化 JSON 获取 Agent 名称"""
        route_map = self.spec.get('route_map', {})
        action = standardized_json.get("action", "chat")
        target = standardized_json.get("target", "text")
        
        key = f"{action}_{target}"
        return route_map.get(key, "chat_agent")
    
    def complete(self, standardized_json: Dict, output_type: str, 
                 output_content: str, output_data: Dict = None) -> Dict:
        """标记任务完成，填充输出"""
        standardized_json["output_type"] = output_type
        standardized_json["output_content"] = output_content
        standardized_json["output_data"] = output_data or {}
        standardized_json["status"] = "completed"
        standardized_json["next"] = "done"
        return standardized_json
    
    def fail(self, standardized_json: Dict, error_msg: str) -> Dict:
        """标记任务失败"""
        standardized_json["status"] = "failed"
        standardized_json["output_content"] = error_msg
        standardized_json["next"] = "wait"
        return standardized_json


unified_parser = UnifiedIntentParser()
