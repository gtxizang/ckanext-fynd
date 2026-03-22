import json
import time

from flask import Blueprint, Response, abort, request

import ckan.plugins.toolkit as toolkit

from ckanext.fynd import protocol
from ckanext.fynd.config import is_enabled

fynd_blueprint = Blueprint("fynd", __name__)

MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # 1MB

# Not thread-safe; per-worker under gunicorn
_request_count = 0
_window_start = time.time()


def _reset_rate_limit():
    global _request_count, _window_start
    _request_count = 0
    _window_start = time.time()


def _check_rate_limit():
    global _request_count, _window_start
    limit = int(toolkit.config.get("ckanext.fynd.rate_limit", "60"))
    if limit == 0:
        return True
    now = time.time()
    if now - _window_start > 60:
        _request_count = 0
        _window_start = now
    _request_count += 1
    return _request_count <= limit


def _jsonrpc_error(req_id, code, message):
    body = {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}
    return Response(json.dumps(body), content_type="application/json")


def _json_response(data, status=200):
    return Response(json.dumps(data, default=str), content_type="application/json", status=status)


@fynd_blueprint.route("/mcp", methods=["POST"])
def mcp_endpoint():
    if not is_enabled():
        abort(404)

    if request.content_length and request.content_length > MAX_CONTENT_LENGTH:
        return _jsonrpc_error(None, -32600, "Request too large")

    if not _check_rate_limit():
        return _jsonrpc_error(None, -32000, "Rate limit exceeded")

    message = request.get_json(silent=True)
    if message is None:
        return _jsonrpc_error(None, -32700, "Parse error")

    context = {
        "user": toolkit.g.user,
        "auth_user_obj": toolkit.g.userobj,
    }
    response = protocol.handle_message(message, context)

    if response is None:
        return Response("", status=204)

    return Response(json.dumps(response), content_type="application/json")


@fynd_blueprint.route("/.well-known/mcp.json", methods=["GET"])
def well_known_mcp():
    site_url = toolkit.config.get("ckan.site_url", "").rstrip("/")
    return _json_response({
        "name": toolkit.config.get("ckan.site_title", "CKAN"),
        "description": "MCP server for {}".format(
            toolkit.config.get("ckan.site_title", "CKAN")
        ),
        "url": "{}/mcp".format(site_url),
        "transport": "streamable-http",
        "capabilities": {"tools": True, "resources": False, "prompts": False},
    })
