#!/usr/bin/env python3
import sys
import json
import requests

def execute(params):
    action = params.get("action")
    
    if action == "health":
        resp = requests.get('http://localhost:8092/api/auth/health')
        return resp.json()
    elif action == "login":
        resp = requests.post('http://localhost:8092/api/auth/login', 
            json={"username": params.get("username"), "password": params.get("password")})
        return resp.json()
    else:
        return {"error": f"Unknown action: {action}"}

if __name__ == "__main__":
    params = json.loads(sys.argv[1])
    print(json.dumps(execute(params)))
