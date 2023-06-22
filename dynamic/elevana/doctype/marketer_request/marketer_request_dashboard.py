from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		'fieldname' : 'marketer_request',
		'non_standard_fieldnames': {
			'Customer': 'ref_docname',
			'Sales Partner': 'ref_docname',
			'Address': 'link_name',
		},
		'transactions': [
			{
				'label': _('Customer'),
				'items': ['Customer']
			},
			{
				'label': _('Address'),
				'items': ['Address']
			},
			{
				'label': _('Sales Partner'),
				'items': ['Sales Partner']
			}
		]
	}
