from flask import Blueprint, jsonify
from services.events_service import get_all_events, get_event

api = Blueprint("api", __name__)


@api.route("/api/events")
def api_events():
    return jsonify(get_all_events())


@api.route("/api/events/<string:event_id>")
def api_event(event_id):

    event = get_event(event_id)

    if event:
        return jsonify(event)

    return jsonify({
        "error": "Sự kiện không tồn tại..."
    }), 404