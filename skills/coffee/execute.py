#!/usr/bin/env python3
import sys
import json
import requests

def execute(params):
    action = params.get("action")
    
    if action == "shops":
        resp = requests.get('http://localhost:8085/api/coffee/shops')
        return resp.json()
    elif action == "order":
        resp = requests.post('http://localhost:8085/api/coffee/order', 
            json={"item": params.get("item", "拿铁"), "shop_id": params.get("shop_id", 1)})
        return resp.json()
    elif action == "menu":
        shop_id = params.get("shop_id", 1)
        resp = requests.get(f'http://localhost:8085/api/coffee/menu?shop_id={shop_id}')
        return resp.json()
    else:
        return {"error": f"Unknown action: {action}"}

if __name__ == "__main__":
    params = json.loads(sys.argv[1])
    print(json.dumps(execute(params)))
