from unittest.mock import patch, MagicMock

from ckanext.fynd.tools import TOOLS


class TestOpenApiToolsDisabled:
    @patch("ckanext.fynd.tools.openapi.openapi_integration_enabled", return_value=False)
    def test_tools_not_registered_when_disabled(self, mock_config):
        # Re-trigger registration
        from ckanext.fynd.tools import openapi
        saved = TOOLS.copy()
        # Remove any openapi tools that might already be registered
        TOOLS[:] = [t for t in TOOLS if t["category"] != "openapi"]
        openapi._registered = False
        openapi.register_if_available()
        names = {t["name"] for t in TOOLS}
        assert "openapi_spec" not in names
        assert "dataset_openapi_spec" not in names
        # Restore
        TOOLS[:] = saved


class TestOpenApiToolsEnabled:
    @patch("ckanext.fynd.tools.openapi._openapi_view_available", return_value=True)
    @patch("ckanext.fynd.tools.openapi.openapi_integration_enabled", return_value=True)
    def test_tools_registered_when_enabled_and_available(self, mock_config, mock_avail):
        from ckanext.fynd.tools import openapi
        saved = TOOLS.copy()
        TOOLS[:] = [t for t in TOOLS if t["category"] != "openapi"]
        openapi._registered = False
        openapi.register_if_available()
        names = {t["name"] for t in TOOLS}
        assert "openapi_spec" in names
        assert "dataset_openapi_spec" in names
        TOOLS[:] = saved

    @patch("ckanext.fynd.tools.openapi._openapi_view_available", return_value=False)
    @patch("ckanext.fynd.tools.openapi.openapi_integration_enabled", return_value=True)
    def test_tools_not_registered_when_extension_missing(self, mock_config, mock_avail):
        from ckanext.fynd.tools import openapi
        saved = TOOLS.copy()
        TOOLS[:] = [t for t in TOOLS if t["category"] != "openapi"]
        openapi._registered = False
        openapi.register_if_available()
        names = {t["name"] for t in TOOLS}
        assert "openapi_spec" not in names
        assert "dataset_openapi_spec" not in names
        TOOLS[:] = saved


class TestOpenApiToolExecution:
    @patch("ckanext.fynd.tools.openapi._openapi_view_available", return_value=True)
    @patch("ckanext.fynd.tools.openapi.openapi_integration_enabled", return_value=True)
    def test_openapi_spec_calls_resource_openapi_show(self, mock_config, mock_avail):
        from ckanext.fynd.tools import openapi
        saved = TOOLS.copy()
        TOOLS[:] = [t for t in TOOLS if t["category"] != "openapi"]
        openapi._registered = False
        openapi.register_if_available()

        tool_def = next(t for t in TOOLS if t["name"] == "openapi_spec")
        mock_backend = MagicMock()
        mock_backend.call_action.return_value = {"openapi": "3.1.0"}
        result = tool_def["handler"](mock_backend, {"resource_id": "abc"}, {"user": ""})
        mock_backend.call_action.assert_called_once_with(
            "resource_openapi_show", {"resource_id": "abc"}, {"user": ""}
        )
        assert result == {"openapi": "3.1.0"}
        TOOLS[:] = saved
