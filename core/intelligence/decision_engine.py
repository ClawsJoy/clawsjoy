from typing import Dict

"""决策引擎 v4 - 配置驱动"""
import json
from pathlib import Path
from datetime import datetime
from core.lib.unified_config import unified_config



class DecisionEngineV4:
    """决策引擎 - 智能决策"""

    VERSION = "4.0.0"

    def __init__(self):
        self.ollama_url = unified_config.get("llm.endpoint", "http://127.0.0.1:11434")
        self.ollama_model = unified_config.get("llm.default_model", unified_config.get("llm.default_model", config_helper.get_llm_model()))
        self.data_dir = Path(unified_config.get("paths.data_root", "data"))
        self.decision_file = self.data_dir / "decisions.json"
        self.rules = self._load_rules()

    def _load_rules(self):
        """加载决策规则"""
        return unified_config.get("decision", {
            "sleep_interval": 0.5,
            "max_queue_size": 100,
            "auto_execute": True
        })

    def decide(self, context: dict) -> dict:
        """根据上下文做决策"""
        task_type = context.get('task_type', 'general')
        
        # 简单决策逻辑
        if task_type == 'math':
            return {"action": "use_math_model", "model": unified_config.get("llm.fast_model", config_helper.get_llm_model(fast=True))}
        elif task_type == 'code':
            return {"action": "use_code_model", "model": unified_config.get("llm.models.code", "deepseek-coder:6.7b")}
        elif task_type == 'creative':
            return {"action": "use_creative_model", "model": unified_config.get("llm.default_model", config_helper.get_llm_model())}
        else:
            return {"action": "use_default_model", "model": self.ollama_model}

    def evaluate(self, condition: dict) -> bool:
        """评估条件"""
        metric = condition.get('metric')
        threshold = condition.get('threshold', 0)
        operator = condition.get('operator', '>=')
        current_value = condition.get('current_value', 0)
        
        if operator == '>=':
            return current_value >= threshold
        elif operator == '<=':
            return current_value <= threshold
        elif operator == '>':
            return current_value > threshold
        elif operator == '<':
            return current_value < threshold
        else:
            return current_value == threshold

    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            "version": self.VERSION,
            "ollama_url": self.ollama_url,
            "ollama_model": self.ollama_model,
            "rules_loaded": True
        }


    def _predict_performance(self) -> Dict:
        """预测性能（集成）"""
        try:
            from core.agents.core.performance_predictor import PerformancePredictor
            predictor = PerformancePredictor()
            # 添加当前指标
            import psutil
            current = {
                'cpu': psutil.cpu_percent(),
                'memory': psutil.virtual_memory().percent,
                'timestamp': datetime.now().isoformat()
            }
            predictor.add_data_point(current)
            return predictor.get_prediction() if hasattr(predictor, 'get_prediction') else {}
        except Exception as e:
            return {"error": str(e), "available": False}

decision_engine = DecisionEngineV4()
