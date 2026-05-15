"""Prometheus 监控指标"""
try:
    from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
    
    REQUEST_COUNT = Counter('clawsjoy_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
    REQUEST_DURATION = Histogram('clawsjoy_request_duration_seconds', 'Request duration', ['method', 'endpoint'])
    ACTIVE_SESSIONS = Gauge('clawsjoy_active_sessions', 'Active sessions')
    SKILL_EXECUTIONS = Counter('clawsjoy_skill_executions_total', 'Skill executions', ['skill', 'status'])
    
    def get_metrics():
        return generate_latest()
        
except ImportError:
    # 如果没有 prometheus_client，返回空指标
    def get_metrics():
        return "# prometheus_client not installed\n"

    CONTENT_TYPE_LATEST = "text/plain; version=0.0.4"
