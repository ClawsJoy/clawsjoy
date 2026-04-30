import sys, json, requests
def execute(params):
    msg = params.get("message", "")
    resp = requests.post('http://localhost:8089/api/router/route', json={"message": msg})
    return resp.json()
if __name__ == "__main__":
    params = json.loads(sys.argv[1])
    print(json.dumps(execute(params)))
