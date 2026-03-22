import json
from unittest.mock import patch, MagicMock

from flask import Flask
from ckanext.fynd.blueprints import fynd_blueprint


def create_test_app():
    app = Flask(__name__)
    app.register_blueprint(fynd_blueprint)
    return app


class TestMcpEndpoint:
    def setup_method(self):
        self.app = create_test_app()
        self.client = self.app.test_client()

    @patch("ckanext.fynd.blueprints.protocol")
    @patch("ckanext.fynd.blueprints.is_enabled", return_value=True)
    @patch("ckanext.fynd.blueprints._check_rate_limit", return_value=True)
    @patch("ckanext.fynd.blueprints.toolkit")
    def test_valid_request(self, mock_tk, mock_rate, mock_enabled, mock_proto):
        mock_tk.g = MagicMock(user="", userobj=None)
        mock_proto.handle_message.return_value = {"jsonrpc": "2.0", "id": 1, "result": {}}
        response = self.client.post(
            "/mcp",
            data=json.dumps({"jsonrpc": "2.0", "method": "ping", "id": 1}),
            content_type="application/json",
        )
        assert response.status_code == 200
        assert json.loads(response.data)["result"] == {}

    @patch("ckanext.fynd.blueprints.is_enabled", return_value=False)
    def test_disabled_returns_404(self, mock_enabled):
        response = self.client.post(
            "/mcp",
            data=json.dumps({"jsonrpc": "2.0", "method": "ping", "id": 1}),
            content_type="application/json",
        )
        assert response.status_code == 404

    @patch("ckanext.fynd.blueprints.is_enabled", return_value=True)
    @patch("ckanext.fynd.blueprints._check_rate_limit", return_value=False)
    def test_rate_limited(self, mock_rate, mock_enabled):
        response = self.client.post(
            "/mcp",
            data=json.dumps({"jsonrpc": "2.0", "method": "ping", "id": 1}),
            content_type="application/json",
        )
        data = json.loads(response.data)
        assert data["error"]["code"] == -32000

    @patch("ckanext.fynd.blueprints.is_enabled", return_value=True)
    @patch("ckanext.fynd.blueprints._check_rate_limit", return_value=True)
    def test_invalid_json(self, mock_rate, mock_enabled):
        response = self.client.post("/mcp", data="not json", content_type="application/json")
        assert json.loads(response.data)["error"]["code"] == -32700

    @patch("ckanext.fynd.blueprints.protocol")
    @patch("ckanext.fynd.blueprints.is_enabled", return_value=True)
    @patch("ckanext.fynd.blueprints._check_rate_limit", return_value=True)
    @patch("ckanext.fynd.blueprints.toolkit")
    def test_notification_returns_204(self, mock_tk, mock_rate, mock_enabled, mock_proto):
        mock_tk.g = MagicMock(user="", userobj=None)
        mock_proto.handle_message.return_value = None
        response = self.client.post(
            "/mcp",
            data=json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}),
            content_type="application/json",
        )
        assert response.status_code == 204


class TestWellKnownMcp:
    def setup_method(self):
        self.app = create_test_app()
        self.client = self.app.test_client()

    @patch("ckanext.fynd.blueprints.toolkit")
    def test_discovery_document(self, mock_tk):
        mock_tk.config.get.side_effect = lambda k, d="": {
            "ckan.site_url": "http://example.com",
            "ckan.site_title": "Test Portal",
        }.get(k, d)
        response = self.client.get("/.well-known/mcp.json")
        data = json.loads(response.data)
        assert data["name"] == "Test Portal"
        assert data["url"] == "http://example.com/mcp"
        assert data["transport"] == "streamable-http"


class TestRateLimiter:
    @patch("ckanext.fynd.blueprints.toolkit")
    def test_blocks_after_limit(self, mock_tk):
        from ckanext.fynd.blueprints import _check_rate_limit, _reset_rate_limit
        mock_tk.config.get.return_value = "5"
        _reset_rate_limit()
        for _ in range(5):
            assert _check_rate_limit() is True
        assert _check_rate_limit() is False
