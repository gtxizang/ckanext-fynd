import logging

import ckan.plugins.toolkit as toolkit

from ckanext.fynd.config import openapi_integration_enabled
from ckanext.fynd.tools import tool

log = logging.getLogger(__name__)

_registered = False


def _openapi_view_available():
    try:
        toolkit.get_action("resource_openapi_show")
        return True
    except Exception:
        return False


def register_if_available():
    global _registered
    if _registered:
        return
    _registered = True

    if not openapi_integration_enabled():
        return
    if not _openapi_view_available():
        log.info("ckanext.fynd.openapi_integration is enabled but "
                 "ckanext-openapi-view is not installed; skipping openapi tools")
        return

    @tool(
        name="openapi_spec",
        description="Get the OpenAPI 3.1 specification for a DataStore resource. "
                    "Returns a full spec with typed schemas, query parameters, "
                    "and endpoint documentation.",
        input_schema={
            "type": "object",
            "properties": {
                "resource_id": {
                    "type": "string",
                    "description": "Resource ID (UUID)",
                },
            },
            "required": ["resource_id"],
        },
        category="openapi",
        auth_action="fynd_openapi_spec",
    )
    def openapi_spec(backend, params, context):
        return backend.call_action("resource_openapi_show", params, context)

    @tool(
        name="dataset_openapi_spec",
        description="Get a combined OpenAPI 3.1 specification covering all "
                    "DataStore resources in a dataset.",
        input_schema={
            "type": "object",
            "properties": {
                "dataset_id": {
                    "type": "string",
                    "description": "Dataset ID (UUID) or name",
                },
            },
            "required": ["dataset_id"],
        },
        category="openapi",
        auth_action="fynd_dataset_openapi_spec",
    )
    def dataset_openapi_spec(backend, params, context):
        return backend.call_action("dataset_openapi_show", params, context)

    log.info("fynd: openapi-view integration tools registered")
