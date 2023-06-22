
from frappe import _


def get_data():
	return {
		'fieldname': 'cheque',
		'non_standard_fieldnames': {
			'Journal Entry': 'cheque',
			'Payment Entry': 'cheque'
		},
		'transactions': [
			{
				'label': _('Payment'),
				'items': ['Payment Entry', 'Journal Entry']
			}
		]
	}
