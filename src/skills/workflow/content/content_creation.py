#!/usr/bin/env python3
"""Content Creation - Content Creation 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

from lib.smart_config import smart_config
"""内容创作工作流"""
from src.lib.base_skill import BaseWorkflowSkill

class ContentCreationWorkflow(BaseWorkflowSkill):
    name = "content_creation"
    description = "内容创作工作流：生成脚本→提取关键词→生成摘要"
    version = "1.0.0"
    category = "workflow"
    
    steps = [
        {"skill": "script_generator", "params": {"topic": "{topic}"}, "output": "script"},
        {"skill": "keyword_extractor", "params": {"text": "{script}"}, "output": "keywords"},
        {"skill": "text_summarizer", "params": {"text": "{script}"}, "output": "summary"}
    ]
    dependencies = ["script_generator", "keyword_extractor", "text_summarizer"]

skill = ContentCreationWorkflow()
