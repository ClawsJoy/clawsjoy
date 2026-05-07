#!/usr/bin/env python3
import sys, json, requests
def execute(params):
    city = params.get("city", "香港")
    style = params.get("style", "科技")
    resp = requests.post('http://localhost:8105/api/promo/make', json={"city": city, "style": style})
    return resp.json()
if __name__ == "__main__":
    params = json.loads(sys.argv[1])
    print(json.dumps(execute(params)))
