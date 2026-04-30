#!/usr/bin/env python3
import sys
import json
import requests

def execute(params):
    action = params.get("action")
    
    if action == "list":
        resp = requests.get('http://localhost:8088/api/tenants')
        return resp.json()
    elif action == "stats":
        resp = requests.get('http://localhost:8088/api/tenants/stats')
        return resp.json()
    else:
        return {"error": f"Unknown action: {action}"}

if __name__ == "__main__":
    params = json.loads(sys.argv[1])
    print(json.dumps(execute(params)))
