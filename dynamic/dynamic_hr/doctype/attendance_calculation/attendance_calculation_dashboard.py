from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		'fieldname' : 'attendance_calculation',
		'non_standard_fieldnames': {
			'Leave Ledger Entry': 'transaction_name',
		},
		'transactions': [
			{
				'label': _('Attendance'),
				'items': ['Attendance']
			},
			{
				'label': _('Additional Salaries'),
				'items': ['Additional Salary']
			},
			{
				'label': _('Leaves'),
				'items': ['Leave Ledger Entry']
			}
		]
	}
