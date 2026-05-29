from flask import jsonify
from lib.agent_bus import get_bus

def register_bus_status_api(app):
    @app.route('/api/bus/status', methods=['GET'])
    def bus_status():
        bus = get_bus()
        return jsonify({
            "message_count": len(bus.message_history),
            "subscribers": bus.subscribers,
            "queue_size": bus.message_queue.qsize(),
            "messages": [
                {"sender": m.sender, "topic": m.topic, "content": m.content}
                for m in bus.message_history[-10:]
            ]
        })
