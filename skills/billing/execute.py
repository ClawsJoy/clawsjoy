#!/usr/bin/env python3
import sys
import json
import requests

def execute(params):
    action = params.get("action")
    tenant_id = params.get("tenant_id", "1")
    
    if action == "balance":
        resp = requests.get(f'http://localhost:8090/api/billing/balance?tenant_id={tenant_id}')
        return resp.json()
    elif action == "usage":
        resp = requests.get(f'http://localhost:8090/api/billing/usage?tenant_id={tenant_id}')
        return resp.json()
    else:
        return {"error": f"Unknown action: {action}"}

if __name__ == "__main__":
    params = json.loads(sys.argv[1])
    print(json.dumps(execute(params)))
