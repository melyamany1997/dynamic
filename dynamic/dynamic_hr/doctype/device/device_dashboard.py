from __future__ import unicode_literals
from frappe import _


def get_data():
    return {
        'fieldname': 'device',
		'non_standard_fieldnames': {
			'Employee Checkin': 'device_id',
			'Device Log': 'parent',
		},
        'transactions': [
            {
                'label': 'Logs',
                'items': ['Employee Checkin', 'Device Log']
            }
        ]
    }
