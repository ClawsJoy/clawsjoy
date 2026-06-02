from flask import Flask, jsonify
from prometheus_client import generate_latest, REGISTRY

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/metrics')
def metrics():
    return generate_latest(REGISTRY)

if __name__ == '__main__':
    app.run(port=5003)
