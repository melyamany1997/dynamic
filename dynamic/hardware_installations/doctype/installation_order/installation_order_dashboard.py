from __future__ import unicode_literals

from frappe import _


def get_data():
    return {
        'fieldname': 'installation_order',
        'non_standard_fieldnames': {
        },

        'internal_links': {
            'Installation Request': 'installation_request'
        },
        'transactions': [
            {
                'label': _('Installation'),
                'items': ['Installation Request', 'Car Installation']
            },
            {
                'label': _('Schedule'),
                'items': ['Employee Schedule']
            },
        ]
    }
