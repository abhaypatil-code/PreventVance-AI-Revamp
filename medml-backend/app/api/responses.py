from flask import jsonify


def ok(payload=None, message=None):
    body = {}
    if message is not None:
        body["message"] = message
    if isinstance(payload, dict):
        body.update(payload)
    elif payload is not None:
        body["data"] = payload
    return jsonify(body), 200


def created(payload=None, message=None):
    body = {}
    if message is not None:
        body["message"] = message
    if isinstance(payload, dict):
        body.update(payload)
    elif payload is not None:
        body["data"] = payload
    return jsonify(body), 201


def bad_request(message="Bad Request", extra=None):
    body = {"error": "Bad Request", "message": message}
    if isinstance(extra, dict):
        body.update(extra)
    return jsonify(body), 400


def unauthorized(message="Unauthorized"):
    return jsonify({"error": "Unauthorized", "message": message}), 401


def forbidden(message="Forbidden"):
    return jsonify({"error": "Forbidden", "message": message}), 403


def not_found(message="Not Found"):
    return jsonify({"error": "Not Found", "message": message}), 404


def conflict(message="Conflict"):
    return jsonify({"error": "Conflict", "message": message}), 409


def unprocessable_entity(messages=None, message="Validation Failed"):
    body = {"error": "Validation Failed", "message": message}
    if messages is not None:
        body["messages"] = messages
    return jsonify(body), 422


def server_error(message="Internal server error"):
    return jsonify({"error": "Internal server error", "message": message}), 500


