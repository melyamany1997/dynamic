from __future__ import unicode_literals

from frappe import _


def get_data():
    return {
        'fieldname': 'installation_request',
        'non_standard_fieldnames': {
        },

        'transactions': [
            {
                'label': _('Installation'),
                'items': ['Installation Order', 'Car Installation']
            },
            {
                'label': _('Schedule'),
                'items': ['Employee Schedule']
            },
        ]
    }
