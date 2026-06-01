"""ClawsJoy v6.0 原子引擎 - 统一入口"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# ========== 导入所有原子引擎 ==========
from engine.semantic.core import semantic_engine
from engine.profile.core import profile_engine
from engine.knowledge.core import knowledge_engine
from engine.skill_matrix.core import skill_matrix_engine
from engine.reasoning.core import reasoning_engine
from engine.planning.core import planning_engine
from engine.memory.core import memory_engine
from engine.active.core import active_engine
from engine.event.core import event_engine
from engine.workflow.core import workflow_engine
from engine.monitor.core import monitor_engine
from engine.scheduler.core import scheduler_engine
from engine.tenant.core import tenant_engine
from engine.ratelimit.core import ratelimit_engine
from engine.audit.core import audit_engine
from engine.hook.core import hook_engine
from engine.document.core import document_engine
from engine.evolution.core import evolution_engine
from engine.common.core import common_engine
from engine.skill_matrix_v2.core import skill_matrix_v2_engine
from engine.embedding.local_embedding import local_embedding
from engine.causal.core import causal_engine
from engine.dynamic_knowledge.core import dynamic_knowledge_engine
from engine.emotion.core import emotion_engine
from engine.proactive.core import proactive_engine
from engine.semantic.enhanced import enhanced_semantic
from engine.learning.core import self_learning_engine
from engine.dialogue.core import dialogue_engine
from engine.recommend.core import recommend_engine
from engine.openclaw.core import openclaw_engine
from engine.orchestration.core import orchestration_engine
from engine.observability.metrics import metrics
from engine.observability.tracer import tracer
from engine.multimodal.vision import vision_engine
from engine.multimodal.audio import audio_engine
from engine.multimodal.video import video_engine

class AtomicEngine:
    """原子引擎 - 统一入口"""

    def __init__(self):
        self._semantic = semantic_engine
        self._profile = profile_engine
        self._knowledge = knowledge_engine
        self._skill = skill_matrix_engine
        self._reasoning = reasoning_engine
        self._planning = planning_engine
        self._memory = memory_engine
        self._active = active_engine
        self._event = event_engine
        self._workflow = workflow_engine
        self._monitor = monitor_engine
        self._scheduler = scheduler_engine
        self._tenant = tenant_engine
        self._ratelimit = ratelimit_engine
        self._audit = audit_engine
        self._hook = hook_engine
        self._document = document_engine
        self._evolution = evolution_engine
        self._common = common_engine
        self._skill_v2 = skill_matrix_v2_engine
        self._embedding = local_embedding
        self._causal = causal_engine
        self._dynamic_knowledge = dynamic_knowledge_engine
        self._emotion = emotion_engine
        self._proactive = proactive_engine
        self._enhanced_semantic = enhanced_semantic
        self._learning = self_learning_engine
        self._dialogue = dialogue_engine
        self._recommend = recommend_engine
        self._openclaw = openclaw_engine
        self._orchestration = orchestration_engine
        self._metrics = metrics
        self._tracer = tracer
        self._vision = vision_engine
        self._audio = audio_engine
        self._video = video_engine
        print("🧠 原子引擎 v6.0 已初始化")

    @property
    def semantic(self):
        return self._semantic

    @property
    def profile(self):
        return self._profile

    @property
    def knowledge(self):
        return self._knowledge

    @property
    def skill(self):
        return self._skill

    @property
    def reasoning(self):
        return self._reasoning

    @property
    def planning(self):
        return self._planning

    @property
    def memory(self):
        return self._memory

    @property
    def active(self):
        return self._active

    @property
    def event(self):
        return self._event

    @property
    def workflow(self):
        return self._workflow

    @property
    def monitor(self):
        return self._monitor

    @property
    def scheduler(self):
        return self._scheduler

    @property
    def tenant(self):
        return self._tenant

    @property
    def ratelimit(self):
        return self._ratelimit

    @property
    def audit(self):
        return self._audit

    @property
    def hook(self):
        return self._hook

    @property
    def document(self):
        return self._document

    @property
    def evolution(self):
        return self._evolution

    @property
    def common(self):
        return self._common

    @property
    def skill_v2(self):
        return self._skill_v2

    @property
    def embedding(self):
        return self._embedding

    @property
    def causal(self):
        return self._causal

    @property
    def dynamic_knowledge(self):
        return self._dynamic_knowledge

    @property
    def emotion(self):
        return self._emotion

    @property
    def proactive(self):
        return self._proactive

    @property
    def enhanced_semantic(self):
        return self._enhanced_semantic

    @property
    def learning(self):
        return self._learning

    @property
    def dialogue(self):
        return self._dialogue

    @property
    def recommend(self):
        return self._recommend

    @property
    def openclaw(self):
        return self._openclaw

    @property
    def orchestration(self):
        return self._orchestration

    @property
    def metrics(self):
        return self._metrics

    @property
    def tracer(self):
        return self._tracer

    @property
    def vision(self):
        return self._vision

    @property
    def audio(self):
        return self._audio

    @property
    def video(self):
        return self._video

engine = AtomicEngine()

__all__ = ['engine']
__version__ = '6.0.0'
