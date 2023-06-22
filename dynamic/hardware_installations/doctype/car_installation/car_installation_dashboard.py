from __future__ import unicode_literals

from frappe import _


def get_data():
    return {
        'fieldname': 'car_installation',
        'non_standard_fieldnames': {
        },

        'internal_links': {
            'Installation Request': 'installation_request' ,
            'Installation Order': 'installation_order' ,
            'Car': 'car' ,
        },
        'transactions': [
            {
                'label': _('Installation'),
                'items': ['Installation Request', 'Installation Order']
            },
            {
                'label': _('Stock'),
                'items': ['Delivery Note']
            },
        ]
    }
