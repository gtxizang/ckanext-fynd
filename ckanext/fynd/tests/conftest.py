import os
import sys
from unittest.mock import MagicMock

import pytest

# Unit tests run without CKAN installed; integration tests use a running instance.
sys.modules.setdefault("ckan", MagicMock())
sys.modules.setdefault("ckan.plugins", MagicMock())
sys.modules.setdefault("ckan.plugins.toolkit", MagicMock())


@pytest.fixture
def ckan_url():
    return os.environ.get("CKAN_TEST_URL", "http://localhost:5050")
