"""元知识管理系统 - 系统自省与自增长"""

from .meta_knowledge import MetaKnowledge
from .skill_generator import SkillGenerator
from .knowledge_grower import KnowledgeGrower

__all__ = ['MetaKnowledge', 'SkillGenerator', 'KnowledgeGrower']

meta_knowledge = MetaKnowledge()
skill_generator = SkillGenerator()
knowledge_grower = KnowledgeGrower()
