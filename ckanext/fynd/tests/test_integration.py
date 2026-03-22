"""Integration tests against a running CKAN instance.

Run with: pytest -m integration
Requires: CKAN at localhost:5050 (or CKAN_TEST_URL env var)
"""
import json
import pytest
import urllib.request
import urllib.error


def _mcp_request(ckan_url, method, params=None, req_id=1):
    """Send an MCP JSON-RPC request to the CKAN instance."""
    message = {"jsonrpc": "2.0", "method": method, "id": req_id}
    if params is not None:
        message["params"] = params
    data = json.dumps(message).encode("utf-8")
    req = urllib.request.Request(
        f"{ckan_url}/mcp",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"http_error": e.code, "body": e.read().decode("utf-8")}


@pytest.mark.integration
class TestMcpInitialize:
    def test_initialize(self, ckan_url):
        response = _mcp_request(ckan_url, "initialize", {"protocolVersion": "2025-03-26"})
        assert "result" in response
        assert response["result"]["protocolVersion"] == "2025-03-26"
        assert response["result"]["serverInfo"]["name"] == "fynd"


@pytest.mark.integration
class TestMcpToolsList:
    def test_lists_tools(self, ckan_url):
        response = _mcp_request(ckan_url, "tools/list")
        assert "result" in response
        tools = response["result"]["tools"]
        assert len(tools) > 0
        names = [t["name"] for t in tools]
        assert "dataset_search" in names
        assert "datastore_search" in names


@pytest.mark.integration
class TestMcpDatasetSearch:
    def test_search_returns_results(self, ckan_url):
        response = _mcp_request(
            ckan_url, "tools/call",
            {"name": "dataset_search", "arguments": {"rows": 5}},
        )
        assert "result" in response
        assert response["result"]["isError"] is False
        content = json.loads(response["result"]["content"][0]["text"])
        assert "count" in content or "results" in content


@pytest.mark.integration
class TestMcpDatasetShow:
    def test_show_existing_dataset(self, ckan_url):
        search = _mcp_request(
            ckan_url, "tools/call",
            {"name": "dataset_search", "arguments": {"rows": 1}},
        )
        content = json.loads(search["result"]["content"][0]["text"])
        if content.get("count", 0) == 0:
            pytest.skip("No datasets on test CKAN")
        dataset_name = content["results"][0]["name"]
        response = _mcp_request(
            ckan_url, "tools/call",
            {"name": "dataset_show", "arguments": {"id": dataset_name}},
        )
        assert response["result"]["isError"] is False


@pytest.mark.integration
class TestMcpOrganizationList:
    def test_lists_organizations(self, ckan_url):
        response = _mcp_request(
            ckan_url, "tools/call",
            {"name": "organization_list", "arguments": {}},
        )
        assert "result" in response
        assert response["result"]["isError"] is False


@pytest.mark.integration
class TestMcpWellKnown:
    def test_discovery_document(self, ckan_url):
        req = urllib.request.Request(f"{ckan_url}/.well-known/mcp.json")
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError:
            pytest.fail("/.well-known/mcp.json returned HTTP error")
        assert "name" in data
        assert "url" in data
        assert data["transport"] == "streamable-http"
        assert data["capabilities"]["tools"] is True
