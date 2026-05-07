import requests, json

def send_webhook(url, data):
    try:
        resp = requests.post(url, json=data, timeout=5)
        return resp.status_code == 200
    except:
        return False
