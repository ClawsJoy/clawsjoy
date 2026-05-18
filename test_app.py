from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/test')
def test():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    print("Starting test server on port 5011...")
    app.run(host='0.0.0.0', port=5011, debug=False)
