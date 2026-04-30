#!/usr/bin/env python3
import sys, json, subprocess
def execute(params):
    keyword = params.get("keyword", "香港")
    count = params.get("count", 5)
    result = subprocess.run(["/home/flybo/clawsjoy/bin/spider_unsplash", keyword, str(count)], capture_output=True)
    return {"success": result.returncode == 0, "output": result.stdout.decode()}
if __name__ == "__main__":
    params = json.loads(sys.argv[1])
    print(json.dumps(execute(params)))
