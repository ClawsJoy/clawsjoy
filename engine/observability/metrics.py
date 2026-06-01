"""指标收集"""

from collections import defaultdict
from datetime import datetime
from typing import Dict, Any

class MetricsCollector:
    def __init__(self):
        self.metrics = defaultdict(list)
    
    def record(self, name: str, value: float, tags: Dict = None):
        self.metrics[name].append({
            "value": value,
            "tags": tags or {},
            "timestamp": datetime.now().isoformat()
        })
        # 保留最近1000条
        if len(self.metrics[name]) > 1000:
            self.metrics[name] = self.metrics[name][-1000:]
    
    def get(self, name: str) -> list:
        return self.metrics.get(name, [])
    
    def get_stats(self) -> Dict:
        return {"metrics_count": len(self.metrics)}

metrics = MetricsCollector()
