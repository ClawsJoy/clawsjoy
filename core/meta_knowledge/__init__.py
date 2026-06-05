#!/usr/bin/env python3
"""Init - Init 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""


from .knowledge_grower import KnowledgeGrower
from .meta_knowledge import MetaKnowledge
from .skill_generator import SkillGenerator

__all__ = ["MetaKnowledge", "SkillGenerator", "KnowledgeGrower"]

meta_knowledge = MetaKnowledge()
skill_generator = SkillGenerator()
knowledge_grower = KnowledgeGrower()
