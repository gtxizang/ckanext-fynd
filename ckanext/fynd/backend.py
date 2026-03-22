import ckan.plugins.toolkit as toolkit


class CkanInternalBackend:

    def call_action(self, action, data_dict, context):
        return toolkit.get_action(action)(context, data_dict)
