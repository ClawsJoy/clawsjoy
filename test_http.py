from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/api/health')
def health():
    return jsonify({"status": "ok", "test": True})

app.run(host='0.0.0.0', port=8080)
