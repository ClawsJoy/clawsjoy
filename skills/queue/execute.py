import sys, json, requests
def execute(params):
    action = params.get("action")
    if action == "stats":
        resp = requests.get('http://localhost:8091/api/queue/stats')
        return resp.json()
    return {"error": "unknown"}
if __name__ == "__main__":
    params = json.loads(sys.argv[1])
    print(json.dumps(execute(params)))
