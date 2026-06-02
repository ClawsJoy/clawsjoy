#!/usr/bin/env python3
"""Translate - Translate 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""


import requests
from core.lib.unified_config import unified_config


class TranslateSkill:
    name = "translate"
    description = "翻译文本"
    version = "1.0.0"
    category = "translate"
    
    def execute(self, params: dict) -> dict:
        text = params.get('text', '')
        target = params.get('target', 'zh')
        source = params.get('source', 'auto')
        
        if not text:
            return {"success": False, "error": "text is required"}
        
        # 构建翻译 prompt
        prompt = f"将以下文本翻译成{target}：\n\n{text}\n\n只输出翻译结果，不要解释。"
        
        # 调用 Ollama
        llm_endpoint = unified_config.get("llm.endpoint", "http://localhost:11434")
        llm_model = unified_config.get("llm.fast_model", "qwen2.5:3b")
        
        try:
            response = requests.post(
                f"{llm_endpoint}/api/generate",
                json={
                    "model": llm_model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                translated = response.json().get('response', '')
                return {
                    "success": True,
                    "translated": translated,
                    "original": text,
                    "target": target
                }
            else:
                return {"success": False, "error": f"翻译失败: {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}


skill = TranslateSkill()
