from core.lib.config_helper import get_data_root, get_llm_endpoint, get_llm_model, get_embedding_model, get_gateway_port, get_timeout
from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config

"""审计师 Agent - 核对数据数量，发现异常"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
from datetime import datetime
from typing import Dict, List

class AuditorAgent:
    """审计师 - 负责核对数据进出数量"""
    
    VERSION = "1.0.0"
    
    def __init__(self):
        self._load_records()
        print(f"📋 审计师 v{self.VERSION} 已启动")
    
    def _load_records(self):
        """加载审计记录"""
        record_file = Path(f"{get_data_root()}/audit_records.json")
        if record_file.exists():
            with open(record_file, 'r') as f:
                self.records = json.load(f)
        else:
            self.records = {
                "vector_operations": [],
                "daily_stats": [],
                "anomalies": []
            }
    
    def _save_records(self):
        record_file = Path(f"{get_data_root()}/audit_records.json")
        record_file.parent.mkdir(parents=True, exist_ok=True)
        with open(record_file, 'w') as f:
            json.dump(self.records, f, indent=2, default=str)
    
    def check_vector_balance(self, operation: str, input_count: int, output_count: int) -> Dict:
        """核对向量库进出数量"""
        is_balanced = input_count == output_count
        anomaly = None
        
        if not is_balanced:
            anomaly = {
                "type": "vector_mismatch",
                "operation": operation,
                "input": input_count,
                "output": output_count,
                "dif": output_count - input_count,
                "timestamp": datetime.now().isoformat()
            }
            self.records["anomalies"].append(anomaly)
        
        self.records["vector_operations"].append({
            "operation": operation,
            "input": input_count,
            "output": output_count,
            "balanced": is_balanced,
            "timestamp": datetime.now().isoformat()
        })
        self._save_records()
        
        return {
            "balanced": is_balanced,
            "input": input_count,
            "output": output_count,
            "dif": output_count - input_count,
            "anomaly": anomaly
        }
    
    def get_daily_report(self) -> Dict:
        """获取每日审计报告"""
        today = datetime.now().strftime("%Y-%m-%d")
        today_ops = [op for op in self.records["vector_operations"] 
                    if op["timestamp"].startswith(today)]
        
        anomalies_today = [a for a in self.records["anomalies"] 
                          if a["timestamp"].startswith(today)]
        
        return {
            "date": today,
            "total_operations": len(today_ops),
            "anomalies_count": len(anomalies_today),
            "anomalies": anomalies_today,
            "status": "⚠️ 有异常" if anomalies_today else "✅ 正常"
        }
    
    def get_stats(self) -> Dict:
        return {
            "total_operations": len(self.records["vector_operations"]),
            "total_anomalies": len(self.records["anomalies"]),
            "latest_anomaly": self.records["anomalies"][-1] if self.records["anomalies"] else None
        }


auditor_agent = AuditorAgent()
