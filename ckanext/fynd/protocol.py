"""JSON-RPC 2.0 message handler for the MCP Streamable HTTP protocol."""
import json
import logging

import ckan.plugins.toolkit as toolkit

from ckanext.fynd.tools import get_tools_for_wire, get_tool_by_name

log = logging.getLogger(__name__)

MCP_PROTOCOL_VERSION = "2025-03-26"
SERVER_NAME = "fynd"
SERVER_VERSION = "0.1.0"


class _InvalidParams(Exception):
    pass


def handle_message(message, context):
    if isinstance(message, list):
        return _handle_batch(message, context)
    return _handle_single(message, context)


def _handle_batch(messages, context):
    responses = []
    for msg in messages:
        response = _handle_single(msg, context)
        if response is not None:
            responses.append(response)
    return responses


def _handle_single(message, context):
    if not isinstance(message, dict):
        return _error_response(None, -32600, "Invalid request")

    jsonrpc = message.get("jsonrpc")
    method = message.get("method")
    req_id = message.get("id")
    params = message.get("params", {})

    if jsonrpc != "2.0" or not method:
        return _error_response(req_id, -32600, "Invalid request")

    is_notification = "id" not in message

    handler = _METHOD_HANDLERS.get(method)
    if handler is None:
        if is_notification:
            return None
        return _error_response(req_id, -32601, f"Method not found: {method}")

    try:
        result = handler(params, context)
    except _InvalidParams as e:
        return _error_response(req_id, -32602, str(e))
    except Exception:
        log.exception("Internal error handling method %s", method)
        return _error_response(req_id, -32603, "Internal error")

    if is_notification:
        return None

    return _success_response(req_id, result)


def _handle_initialize(params, context):
    return {
        "protocolVersion": MCP_PROTOCOL_VERSION,
        "capabilities": {
            "tools": {"listChanged": False},
        },
        "serverInfo": {
            "name": SERVER_NAME,
            "version": SERVER_VERSION,
        },
    }


def _handle_notifications_initialized(params, context):
    return None


def _handle_ping(params, context):
    return {}


def _handle_tools_list(params, context):
    return {"tools": get_tools_for_wire()}


def _handle_tools_call(params, context):
    name = params.get("name")
    if not name:
        raise _InvalidParams("Missing required parameter: name")

    arguments = params.get("arguments", {})

    tool_def = get_tool_by_name(name)
    if tool_def is None:
        raise _InvalidParams(f"Unknown tool: {name}")

    try:
        toolkit.check_access(tool_def["auth_action"], context, arguments)
    except toolkit.NotAuthorized:
        return _tool_error("Not found or not authorized")

    try:
        from ckanext.fynd.backend import CkanInternalBackend
        backend = CkanInternalBackend()
        result = tool_def["handler"](backend, arguments, context)
        return _tool_result(result)
    except toolkit.ObjectNotFound:
        return _tool_error("Not found or not authorized")
    except toolkit.NotAuthorized:
        return _tool_error("Not found or not authorized")
    except toolkit.ValidationError as e:
        return _tool_error(f"Validation error: {e}")
    except Exception:
        log.exception("Error executing tool %s", name)
        return _tool_error("Internal server error")


_METHOD_HANDLERS = {
    "initialize": _handle_initialize,
    "notifications/initialized": _handle_notifications_initialized,
    "ping": _handle_ping,
    "tools/list": _handle_tools_list,
    "tools/call": _handle_tools_call,
}


def _success_response(req_id, result):
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def _error_response(req_id, code, message):
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


def _tool_result(data):
    return {
        "content": [{"type": "text", "text": json.dumps(data, default=str)}],
        "isError": False,
    }


def _tool_error(message):
    return {
        "content": [{"type": "text", "text": f"Error: {message}"}],
        "isError": True,
    }
