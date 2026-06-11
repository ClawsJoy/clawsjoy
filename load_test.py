#!/usr/bin/env python3
"""简单负载测试"""

import time
import threading
import requests
from concurrent.futures import ThreadPoolExecutor

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiZDE2YjIwYjJjZWRjZjNjZiIsInVzZXJuYW1lIjoidGVzdHVzZXIiLCJyb2xlIjoidXNlciIsImV4cCI6MTc4MTE4MzMyMn0.2cbQMYnwasdm1cxjxtUuhJyODjaF4GyXoHdma-TZnzQ"
URL = "http://localhost:5002/api/v5/enhanced/chat"

def make_request():
    try:
        resp = requests.post(URL, 
            headers={"Authorization": f"Bearer {TOKEN}"},
            json={"message": "1+1", "user_id": "load_test"},
            timeout=30)
        return resp.status_code == 200
    except:
        return False

def run_load_test(concurrent=10, total=100):
    print(f"负载测试: {concurrent} 并发, {total} 总请求")
    
    start = time.time()
    with ThreadPoolExecutor(max_workers=concurrent) as executor:
        futures = [executor.submit(make_request) for _ in range(total)]
        results = [f.result() for f in futures]
    
    elapsed = time.time() - start
    success = sum(results)
    
    print(f"完成: {elapsed:.2f}s")
    print(f"成功: {success}/{total}")
    print(f"QPS: {total/elapsed:.2f}")

if __name__ == "__main__":
    run_load_test(concurrent=10, total=50)
