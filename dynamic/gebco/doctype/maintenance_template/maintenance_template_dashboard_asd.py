from __future__ import unicode_literals

from frappe import _


def get_data():
	return {
		'fieldname': 'maintenance_template',
		'non_standard_fieldnames': {
			'Sales Invoice': 'maintenance_template',
			'Delivery Note': 'maintenance_template',
            'Stock Entry': 'maintenance_template',
		},

		'transactions': [
			{
				'label': _('Selling'),
				'items': ['Sales Invoice', 'Delivery Note']
			},
            {
				'label': _('Stock'),
				'items': ['Stock Entry']
			},	
		]
	}
