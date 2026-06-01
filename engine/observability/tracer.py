"""链路追踪"""

from contextvars import ContextVar
from datetime import datetime
import uuid
from typing import Dict, Any

trace_id_var: ContextVar = ContextVar('trace_id', default='')

class Tracer:
    def __init__(self):
        self.traces = []
    
    def start_span(self, name: str, parent_id: str = None) -> str:
        trace_id = str(uuid.uuid4())
        self.traces.append({
            "name": name,
            "trace_id": trace_id,
            "parent_id": parent_id,
            "start": datetime.now().isoformat()
        })
        trace_id_var.set(trace_id)
        return trace_id
    
    def end_span(self, trace_id: str):
        for trace in self.traces:
            if trace["trace_id"] == trace_id:
                trace["end"] = datetime.now().isoformat()
                break
    
    def get_stats(self) -> Dict:
        return {"total_spans": len(self.traces)}

tracer = Tracer()
