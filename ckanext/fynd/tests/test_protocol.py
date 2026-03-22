import json
from unittest.mock import patch, MagicMock

from ckanext.fynd.protocol import handle_message

MCP_PROTOCOL_VERSION = "2025-03-26"


def jsonrpc_request(method, params=None, req_id=1):
    msg = {"jsonrpc": "2.0", "method": method, "id": req_id}
    if params is not None:
        msg["params"] = params
    return msg


def jsonrpc_notification(method, params=None):
    msg = {"jsonrpc": "2.0", "method": method}
    if params is not None:
        msg["params"] = params
    return msg


class TestInitialize:
    def test_returns_server_info(self):
        msg = jsonrpc_request("initialize", {"protocolVersion": MCP_PROTOCOL_VERSION})
        response = handle_message(msg, {"user": "", "auth_user_obj": None})
        assert response["result"]["protocolVersion"] == MCP_PROTOCOL_VERSION
        assert response["result"]["serverInfo"]["name"] == "fynd"
        assert response["result"]["capabilities"]["tools"]["listChanged"] is False

    def test_response_id_matches_request(self):
        msg = jsonrpc_request("initialize", {"protocolVersion": MCP_PROTOCOL_VERSION}, req_id=42)
        response = handle_message(msg, {"user": "", "auth_user_obj": None})
        assert response["id"] == 42


class TestNotificationsInitialized:
    def test_returns_none(self):
        msg = jsonrpc_notification("notifications/initialized")
        assert handle_message(msg, {"user": "", "auth_user_obj": None}) is None


class TestPing:
    def test_returns_empty_result(self):
        response = handle_message(jsonrpc_request("ping"), {"user": "", "auth_user_obj": None})
        assert response["result"] == {}


class TestToolsList:
    @patch("ckanext.fynd.protocol.get_tools_for_wire")
    def test_returns_tools(self, mock_wire):
        mock_wire.return_value = [
            {"name": "dataset_search", "description": "Search", "inputSchema": {}}
        ]
        response = handle_message(
            jsonrpc_request("tools/list"), {"user": "", "auth_user_obj": None}
        )
        assert response["result"]["tools"] == mock_wire.return_value


class TestToolsCall:
    @patch("ckanext.fynd.protocol.get_tool_by_name")
    def test_calls_handler_and_wraps_result(self, mock_get_tool):
        mock_handler = MagicMock(return_value={"count": 5, "results": []})
        mock_get_tool.return_value = {
            "name": "dataset_search",
            "auth_action": "fynd_dataset_search",
            "handler": mock_handler,
        }
        msg = jsonrpc_request("tools/call", {"name": "dataset_search", "arguments": {"q": "test"}})
        with patch("ckanext.fynd.protocol.toolkit") as mock_tk:
            mock_tk.check_access.return_value = True
            response = handle_message(msg, {"user": "admin", "auth_user_obj": None})
        assert response["result"]["isError"] is False
        content = json.loads(response["result"]["content"][0]["text"])
        assert content["count"] == 5

    @patch("ckanext.fynd.protocol.get_tool_by_name", return_value=None)
    def test_unknown_tool(self, mock_get_tool):
        msg = jsonrpc_request("tools/call", {"name": "nonexistent", "arguments": {}})
        response = handle_message(msg, {"user": "", "auth_user_obj": None})
        assert response["error"]["code"] == -32602

    @patch("ckanext.fynd.protocol.get_tool_by_name")
    def test_auth_failure(self, mock_get_tool):
        mock_get_tool.return_value = {
            "name": "dataset_show",
            "auth_action": "fynd_dataset_show",
            "handler": MagicMock(),
        }
        msg = jsonrpc_request("tools/call", {"name": "dataset_show", "arguments": {"id": "x"}})
        with patch("ckanext.fynd.protocol.toolkit") as mock_tk:
            mock_tk.NotAuthorized = Exception
            mock_tk.ObjectNotFound = KeyError
            mock_tk.check_access.side_effect = Exception("denied")
            response = handle_message(msg, {"user": "", "auth_user_obj": None})
        assert response["result"]["isError"] is True

    @patch("ckanext.fynd.protocol.get_tool_by_name")
    def test_not_found_same_error_as_auth_failure(self, mock_get_tool):
        mock_handler = MagicMock()
        mock_get_tool.return_value = {
            "name": "dataset_show",
            "auth_action": "fynd_dataset_show",
            "handler": mock_handler,
        }
        msg = jsonrpc_request("tools/call", {"name": "dataset_show", "arguments": {"id": "x"}})
        with patch("ckanext.fynd.protocol.toolkit") as mock_tk:
            mock_tk.NotAuthorized = Exception
            mock_tk.ObjectNotFound = KeyError
            mock_tk.check_access.return_value = True
            mock_handler.side_effect = KeyError("not found")
            response = handle_message(msg, {"user": "", "auth_user_obj": None})
        assert response["result"]["isError"] is True
        assert "not found or not authorized" in response["result"]["content"][0]["text"].lower()

    def test_missing_name_param(self):
        msg = jsonrpc_request("tools/call", {"arguments": {}})
        response = handle_message(msg, {"user": "", "auth_user_obj": None})
        assert response["error"]["code"] == -32602


class TestMethodNotFound:
    def test_unknown_method(self):
        response = handle_message(
            jsonrpc_request("unknown/method"), {"user": "", "auth_user_obj": None}
        )
        assert response["error"]["code"] == -32601


class TestBatchRequests:
    def test_returns_batch(self):
        batch = [jsonrpc_request("ping", req_id=1), jsonrpc_request("ping", req_id=2)]
        response = handle_message(batch, {"user": "", "auth_user_obj": None})
        assert isinstance(response, list)
        assert len(response) == 2

    def test_notification_omitted_from_response(self):
        batch = [jsonrpc_request("ping", req_id=1), jsonrpc_notification("notifications/initialized")]
        response = handle_message(batch, {"user": "", "auth_user_obj": None})
        assert len(response) == 1

    def test_one_error_doesnt_fail_batch(self):
        batch = [jsonrpc_request("ping", req_id=1), jsonrpc_request("unknown/method", req_id=2)]
        response = handle_message(batch, {"user": "", "auth_user_obj": None})
        assert response[0]["result"] == {}
        assert response[1]["error"]["code"] == -32601


class TestMalformedRequests:
    def test_missing_jsonrpc_field(self):
        response = handle_message({"method": "ping", "id": 1}, {"user": "", "auth_user_obj": None})
        assert response["error"]["code"] == -32600

    def test_missing_method_field(self):
        response = handle_message({"jsonrpc": "2.0", "id": 1}, {"user": "", "auth_user_obj": None})
        assert response["error"]["code"] == -32600
