from unittest.mock import patch

from ckanext.fynd.config import is_enabled, enabled_tool_categories, datastore_max_rows


class TestIsEnabled:
    @patch("ckanext.fynd.config.toolkit")
    def test_enabled_by_default(self, mock_toolkit):
        mock_toolkit.config.get.return_value = "true"
        mock_toolkit.asbool.return_value = True
        assert is_enabled() is True

    @patch("ckanext.fynd.config.toolkit")
    def test_disabled_when_false(self, mock_toolkit):
        mock_toolkit.config.get.return_value = "false"
        mock_toolkit.asbool.return_value = False
        assert is_enabled() is False


class TestEnabledToolCategories:
    @patch("ckanext.fynd.config.toolkit")
    def test_default_categories(self, mock_toolkit):
        mock_toolkit.config.get.return_value = "datasets datastore organisations groups tags"
        result = enabled_tool_categories()
        assert result == {"datasets", "datastore", "organisations", "groups", "tags"}

    @patch("ckanext.fynd.config.toolkit")
    def test_subset(self, mock_toolkit):
        mock_toolkit.config.get.return_value = "datasets datastore"
        assert enabled_tool_categories() == {"datasets", "datastore"}

    @patch("ckanext.fynd.config.toolkit")
    def test_empty_string(self, mock_toolkit):
        mock_toolkit.config.get.return_value = ""
        assert enabled_tool_categories() == set()


class TestDatastoreMaxRows:
    @patch("ckanext.fynd.config.toolkit")
    def test_parses_int(self, mock_toolkit):
        mock_toolkit.config.get.return_value = "50"
        assert datastore_max_rows() == 50
