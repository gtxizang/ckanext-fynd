"""Main plugin -- wires together blueprints, auth, and tool registration."""
import ckan.plugins as plugins

from ckanext.fynd.auth import get_auth_functions
from ckanext.fynd.blueprints import fynd_blueprint
from ckanext.fynd.tools.openapi import register_if_available

import ckanext.fynd.tools.datasets  # noqa: F401
import ckanext.fynd.tools.datastore  # noqa: F401
import ckanext.fynd.tools.resources  # noqa: F401
import ckanext.fynd.tools.organisations  # noqa: F401
import ckanext.fynd.tools.groups  # noqa: F401
import ckanext.fynd.tools.tags  # noqa: F401


class FyndPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IAuthFunctions)

    # IBlueprint

    def get_blueprint(self):
        # Deferred to here because config isn't available at import time
        register_if_available()
        return [fynd_blueprint]

    # IAuthFunctions

    def get_auth_functions(self):
        return get_auth_functions()
