import json, time, redis
from datetime import datetime

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

def save_workflow_result(workflow_id, tenant_id, result):
    key = f"workflow:history:{tenant_id}:{workflow_id}"
    data = {
        "workflow_id": workflow_id,
        "tenant_id": tenant_id,
        "result": json.dumps(result, ensure_ascii=False),
        "timestamp": datetime.now().isoformat()
    }
    redis_client.hset(key, mapping=data)
    redis_client.expire(key, 86400 * 7)  # 保留7天
    return True

def get_workflow_history(tenant_id, limit=10):
    keys = redis_client.keys(f"workflow:history:{tenant_id}:*")
    history = []
    for key in keys[-limit:]:
        data = redis_client.hgetall(key)
        if data:
            history.append({
                "workflow_id": data.get("workflow_id"),
                "timestamp": data.get("timestamp"),
                "result": json.loads(data.get("result", "{}"))
            })
    return history
