from unittest.mock import patch

from ckanext.fynd.auth import get_auth_functions


class TestAuthFunctions:
    def test_all_tools_have_auth(self):
        with patch("ckanext.fynd.auth.toolkit") as mock_tk:
            mock_tk.auth_allow_anonymous_access = lambda fn: fn
            funcs = get_auth_functions()
        expected_core = {
            "fynd_dataset_search", "fynd_dataset_show", "fynd_dataset_list",
            "fynd_datastore_search", "fynd_datastore_fields",
            "fynd_resource_show",
            "fynd_organization_list", "fynd_organization_show",
            "fynd_group_list", "fynd_group_show",
            "fynd_tag_list",
        }
        assert expected_core.issubset(set(funcs.keys()))

    @patch("ckanext.fynd.auth.toolkit")
    def test_public_access_succeeds(self, mock_toolkit):
        mock_toolkit.check_access.return_value = True
        mock_toolkit.NotAuthorized = Exception
        mock_toolkit.auth_allow_anonymous_access = lambda fn: fn

        funcs = get_auth_functions()
        result = funcs["fynd_dataset_search"]({"user": ""}, {})
        assert result["success"] is True

    @patch("ckanext.fynd.auth.toolkit")
    def test_unauthorized_returns_failure(self, mock_toolkit):
        mock_toolkit.NotAuthorized = Exception
        mock_toolkit.check_access.side_effect = Exception("denied")
        mock_toolkit.auth_allow_anonymous_access = lambda fn: fn

        funcs = get_auth_functions()
        result = funcs["fynd_dataset_show"]({"user": ""}, {"id": "private"})
        assert result["success"] is False
        assert "msg" in result
