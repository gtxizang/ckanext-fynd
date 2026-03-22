import pytest
from unittest.mock import patch, MagicMock

from ckanext.fynd.tools import TOOLS, tool, get_enabled_tools, get_tools_for_wire
from ckanext.fynd.backend import CkanInternalBackend

import ckanext.fynd.tools.datasets  # noqa: F401
import ckanext.fynd.tools.datastore  # noqa: F401
import ckanext.fynd.tools.resources  # noqa: F401
import ckanext.fynd.tools.organisations  # noqa: F401
import ckanext.fynd.tools.groups  # noqa: F401
import ckanext.fynd.tools.tags  # noqa: F401


@pytest.fixture
def clean_registry():
    saved = TOOLS.copy()
    TOOLS.clear()
    yield
    TOOLS.clear()
    TOOLS.extend(saved)


class TestToolDecorator:
    def test_registers_tool(self, clean_registry):
        @tool(name="test_tool", description="A test", input_schema={},
              category="test", auth_action="test_action")
        def handler(backend, params, context):
            return {"ok": True}

        assert len(TOOLS) == 1
        assert TOOLS[0]["name"] == "test_tool"
        assert TOOLS[0]["handler"] is handler


class TestGetEnabledTools:
    @patch("ckanext.fynd.tools.enabled_tool_categories", return_value={"datasets"})
    def test_filters_by_category(self, mock_cats, clean_registry):
        @tool(name="ds", description="", input_schema={}, category="datasets", auth_action="a")
        def h1(b, p, c):
            pass

        @tool(name="org", description="", input_schema={}, category="organisations", auth_action="b")
        def h2(b, p, c):
            pass

        enabled = get_enabled_tools()
        assert len(enabled) == 1
        assert enabled[0]["name"] == "ds"


class TestGetToolsForWire:
    @patch("ckanext.fynd.tools.enabled_tool_categories", return_value={"datasets"})
    def test_strips_internal_fields(self, mock_cats, clean_registry):
        @tool(name="dataset_search", description="Search datasets",
              input_schema={"type": "object"}, category="datasets",
              auth_action="fynd_dataset_search")
        def h(b, p, c):
            pass

        wire = get_tools_for_wire()
        assert len(wire) == 1
        assert set(wire[0].keys()) == {"name", "description", "inputSchema"}


class TestCkanInternalBackend:
    def test_delegates_to_get_action(self):
        mock_result = {"count": 5, "results": []}
        with patch("ckanext.fynd.backend.toolkit") as mock_toolkit:
            mock_toolkit.get_action.return_value = lambda ctx, dd: mock_result
            backend = CkanInternalBackend()
            result = backend.call_action("package_search", {"q": "test"}, {"user": "test"})
        mock_toolkit.get_action.assert_called_once_with("package_search")
        assert result == mock_result


EXPECTED_TOOLS = {
    "dataset_search", "dataset_show", "dataset_list",
    "datastore_search", "datastore_fields",
    "resource_show",
    "organization_list", "organization_show",
    "group_list", "group_show",
    "tag_list",
}


class TestToolRegistration:
    def test_all_tools_registered(self):
        registered = {t["name"] for t in TOOLS}
        assert registered == EXPECTED_TOOLS

    def test_dataset_search_calls_package_search(self):
        tool_def = next(t for t in TOOLS if t["name"] == "dataset_search")
        mock_backend = MagicMock()
        mock_backend.call_action.return_value = {"count": 0, "results": []}
        tool_def["handler"](mock_backend, {"q": "energy"}, {"user": ""})
        mock_backend.call_action.assert_called_once_with(
            "package_search", {"q": "energy"}, {"user": ""}
        )

    @patch("ckanext.fynd.tools.datastore.datastore_max_rows", return_value=50)
    def test_datastore_search_caps_rows(self, mock_max):
        tool_def = next(t for t in TOOLS if t["name"] == "datastore_search")
        mock_backend = MagicMock()
        mock_backend.call_action.return_value = {"records": []}
        tool_def["handler"](mock_backend, {"resource_id": "abc", "limit": 200}, {"user": ""})
        assert mock_backend.call_action.call_args[0][1]["limit"] == 50

    def test_datastore_fields_returns_only_fields(self):
        tool_def = next(t for t in TOOLS if t["name"] == "datastore_fields")
        mock_backend = MagicMock()
        mock_backend.call_action.return_value = {
            "fields": [{"id": "name", "type": "text"}],
            "records": [],
        }
        result = tool_def["handler"](mock_backend, {"resource_id": "abc"}, {"user": ""})
        assert mock_backend.call_action.call_args[0][1]["limit"] == 0
        assert "fields" in result
        assert "records" not in result
