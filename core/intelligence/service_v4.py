"""统一智能服务 v4.0.0 - 整合所有智能能力"""

import sys
from pathlib import Path
from typing import Dict, Any

sys.path.insert(0, str(Path(__file__).parent.parent))

from intelligence.registry_v4 import registry
from core.lib.config_loader import config


class IntelligenceServiceV4:
    """统一智能服务 - 整合所有现有智能模块"""
    
    VERSION = "4.0.0"
    
    def __init__(self):
        self.registry = registry
        self._init_services()
    
    def _init_services(self):
        """初始化各服务"""
        # 预测服务
        predictor_module = self.registry.get('predictor')
        self.predict = predictor_module.predict if predictor_module and hasattr(predictor_module, 'predict') else self._default_predict
        
        # 决策服务
        decision_module = self.registry.get('decision_engine')
        self.decide = decision_module.decide if decision_module and hasattr(decision_module, 'decide') else self._default_decide
        
        # 学习服务
        learner_module = self.registry.get('learner')
        self.learn = learner_module.learn if learner_module and hasattr(learner_module, 'learn') else self._default_learn
        
        # 闭环服务
        loop_module = self.registry.get('closed_loop')
        self.run_loop = loop_module.run if loop_module and hasattr(loop_module, 'run') else self._default_loop
        
        # 监控服务
        monitor_module = self.registry.get('success_monitor')
        self.monitor = monitor_module.check_and_alert if monitor_module and hasattr(monitor_module, 'check_and_alert') else self._default_monitor
    
    def _default_predict(self, task_name: str) -> dict:
        return {"task": task_name, "rate": 0.5, "confidence": 0.5}
    
    def _default_decide(self, context: dict) -> dict:
        return {"action": "defer", "reason": "default decision"}
    
    def _default_learn(self, pattern: str, outcome: str) -> bool:
        return False
    
    def _default_loop(self) -> dict:
        return {"status": "idle"}
    
    def _default_monitor(self) -> dict:
        return {"rate": 0, "level": "unknown"}
    
    def get_status(self) -> Dict:
        """获取服务状态"""
        return {
            "version": self.VERSION,
            "modules": self.registry.list_modules(),
            "config": {
                "quality_threshold": config.get('thresholds.quality_min_score', 0.5),
                "smart_scheduling": config.is_enabled('enable_smart_scheduling')
            }
        }
    
    def analyze_task(self, task_name: str) -> Dict:
        """综合分析任务"""
        prediction = self.predict(task_name)
        decision = self.decide({"task_name": task_name})
        
        return {
            "task": task_name,
            "prediction": prediction,
            "decision": decision,
            "recommendation": self._get_recommendation(prediction, decision)
        }
    
    def _get_recommendation(self, prediction: dict, decision: dict) -> str:
        rate = prediction.get('rate', 0.5)
        if rate >= 0.8:
            return "立即执行"
        elif rate >= 0.5:
            return "正常调度"
        else:
            return "建议延迟或优化"


intelligence_service = IntelligenceServiceV4()


if __name__ == "__main__":
    print(f"智能服务 v{intelligence_service.VERSION}")
    print(f"状态: {intelligence_service.get_status()}")
    
    # 测试分析
    result = intelligence_service.analyze_task("香港高才通")
    print(f"\n分析结果: {result}")
