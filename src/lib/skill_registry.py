#!/usr/bin/env python3
"""Skill Registry - Skill Registry 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

from lib.smart_config import smart_config
"""技能注册器 - 符合 OpenClaw 规范"""
import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field

@dataclass
class SkillManifest:
    name: str
    type: str
    version: str
    description: str
    category: str
    author: str = "ClawsJoy"
    tags: List[str] = field(default_factory=list)
    compatible_with: List[str] = field(default_factory=lambda: ["openclaw", "clawsjoy"])
    input_schema: Dict = field(default_factory=dict)
    output_schema: Dict = field(default_factory=dict)
    llm_prompt_template: str = ""
    examples: List[Dict] = field(default_factory=list)
    steps: List[Dict] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "type": self.type,
            "version": self.version,
            "description": self.description,
            "category": self.category,
            "author": self.author,
            "tags": self.tags,
            "compatible_with": self.compatible_with,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "llm_prompt_template": self.llm_prompt_template,
            "examples": self.examples,
            "steps": self.steps,
            "dependencies": self.dependencies
        }
    
    def get_llm_description(self) -> str:
        return f"- {self.name}: {self.description} (参数: {list(self.input_schema.keys())})"

class SkillRegistry:
    def __init__(self, manifests_dir="src/skills/manifests"):
        self.manifests_dir = Path(manifests_dir)
        self.atomic_skills: Dict[str, SkillManifest] = {}
        self.workflows: Dict[str, SkillManifest] = {}
        self._load_all()
    
    def _load_all(self):
        self.manifests_dir.mkdir(parents=True, exist_ok=True)
        
        atomic_dir = self.manifests_dir / "atomic"
        if atomic_dir.exists():
            for f in atomic_dir.glob("*.json"):
                with open(f) as fp:
                    data = json.load(fp)
                    manifest = SkillManifest(**data)
                    self.atomic_skills[manifest.name] = manifest
                    print(f"✅ 加载原子技能: {manifest.name}")
        
        workflow_dir = self.manifests_dir / "workflow"
        if workflow_dir.exists():
            for f in workflow_dir.glob("*.json"):
                with open(f) as fp:
                    data = json.load(fp)
                    manifest = SkillManifest(**data)
                    self.workflows[manifest.name] = manifest
                    print(f"✅ 加载工作流: {manifest.name}")
    
    def get_skills_for_llm(self) -> str:
        lines = ["可用技能:"]
        for skill in self.atomic_skills.values():
            lines.append(skill.get_llm_description())
        for wf in self.workflows.values():
            lines.append(wf.get_llm_description())
        return "\n".join(lines)
    
    def list_all(self) -> List[str]:
        return list(self.atomic_skills.keys()) + list(self.workflows.keys())
    
    def get(self, name: str) -> Optional[SkillManifest]:
        return self.atomic_skills.get(name) or self.workflows.get(name)

skill_registry = SkillRegistry()
