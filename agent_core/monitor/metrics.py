import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class MetricsCollector:
    def __init__(self):
        self.metrics_file = Path("data/metrics.json")
        self.metrics = self._load()
    
    def _load(self):
        if self.metrics_file.exists():
            with open(self.metrics_file, 'r') as f:
                return json.load(f)
        return {'api_calls': [], 'errors': [], 'stats': {}}
    
    def _save(self):
        with open(self.metrics_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
    
    def record_api_call(self, endpoint: str, duration_ms: float, status: int):
        self.metrics['api_calls'].append({
            'endpoint': endpoint, 'duration_ms': duration_ms,
            'status': status, 'timestamp': datetime.now().isoformat()
        })
        self.metrics['api_calls'] = self.metrics['api_calls'][-1000:]
        
        # 更新统计
        if endpoint not in self.metrics['stats']:
            self.metrics['stats'][endpoint] = {'count': 0, 'total_ms': 0, 'errors': 0}
        self.metrics['stats'][endpoint]['count'] += 1
        self.metrics['stats'][endpoint]['total_ms'] += duration_ms
        if status >= 400:
            self.metrics['stats'][endpoint]['errors'] += 1
        self._save()
    
    def get_stats(self):
        result = {}
        for ep, stat in self.metrics['stats'].items():
            result[ep] = {
                'count': stat['count'],
                'avg_ms': round(stat['total_ms'] / max(1, stat['count']), 2),
                'error_rate': round(stat['errors'] / max(1, stat['count']) * 100, 2)
            }
        return result

metrics = MetricsCollector()
