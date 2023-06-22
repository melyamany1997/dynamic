# Copyright (c) 2022, Dynamic and contributors
# For license information, please see license.txt


import frappe
from datetime import date
import datetime
from frappe.utils import add_to_date
from frappe.utils import getdate
from frappe.utils import pretty_date, now, add_to_date
from erpnext.accounts.utils import get_balance_on
from operator import itemgetter
from frappe import _
from dynamic.cheques.doctype.cheque.cheque import cheque_status


def execute(filters=None):
    return Cheques_summary_report(filters).run() 


class Cheques_summary_report(object):
	def __init__(self, filters=None):
		self.filters = frappe._dict(filters or {})

	def run(self):
		self.get_columns()
		self.get_data()

		return self.columns, self.data

	def get_columns(self):
		# add columns wich appear data
		self.columns = [
			{
				"fieldname": "party_type",
				"fieldtype": "Data",
				"label": _("Party Type"),
				"width": 150
			},
			{
				"fieldname": "party",
				"fieldtype": "Data",
				"label": _("Party"),
				"width": 150
			},
			{
				"fieldname": "total_count",
				"fieldtype": "Float",
				"label": _("Total Count"),
				"width": 120

			},
			{
				"fieldname": "total_amount",
				"fieldtype": "Float",
				"label": _("Total Amount"),
				"width": 120

			},
		]

		for c_status in cheque_status:
			if not self.filters.get('attributes') or self.filters.get('attributes') in ['Count', 'Both', None]:
				self.columns.append({
					"fieldname": c_status.replace(' ', '_').lower() + "_count",
					"fieldtype": "Float",
					"label": _(c_status)+ " " + _("Amount"),
					"width": 150
				})
			if not self.filters.get('attributes') or self.filters.get('attributes') in ['Amount', 'Both', None]:
				self.columns.append({
					"fieldname": c_status.replace(' ', '_').lower() + "_amount",
					"fieldtype": "Float",
					"label": _(c_status) + " " + _("Amount"),
					"width": 150
				})

	
		return self.columns

	def get_data(self):
		self.data = []
		# frappe.errprint(f'filters->{self.filters}')
		self.conditions, self.values = self.get_conditions(self.filters)
		self.data = self.get_data_from_payment_entry_amount(
			self.conditions, self.values)
		return self.data

	def get_data_from_payment_entry_amount(self, conditions='', values=''):
		columns_str = ""

		for c_status in cheque_status:
			if not self.filters.get('attributes') or self.filters.get('attributes') == ['Count', 'Both', None]:
				c_name = c_status.replace(' ', '_').lower() + "_count"
				columns_str += f"""
				, SUM(CASE	WHEN cheque_status = "{c_status}" 
							THEN 1 
							ELSE 0 
							END) AS `{c_name}`
				 """
	
			if not self.filters.get('attributes') or self.filters.get('attributes') in ['Amount', 'Both', None]:
				c_name = c_status.replace(' ', '_').lower() + "_amount"
				columns_str += f"""
				, SUM(CASE	WHEN cheque_status = "{c_status}" 
							THEN paid_amount
							ELSE 0 
							END) AS `{c_name}`
				 """

		query_test_p = f"""
		select party_type,party,count(cheque) as `total_count`,sum(paid_amount) as total_amount
		{columns_str}
		from `tabPayment Entry` p 
		WHERE {conditions} group by party
		"""

		data_dict_p = frappe.db.sql(query_test_p, values=values, as_dict=1)
		return data_dict_p

	def get_conditions(self, filters):
		conditions = "1=1 "
		values = dict()
		if filters.get("cheque_status"):
			if filters.get("cheque_status") == 'Rejected' or filters.get("cheque_status") == "Rejected in Bank":
				# AND p.docstatus = '2'
				conditions += " AND p.cheque_status =  %(cheque_status)s "
			else:
				conditions += " AND p.cheque_status =  %(cheque_status)s AND p.docstatus = '1' "
			values["cheque_status"] = filters.get("cheque_status")

		if filters.get('party'):
			conditions += " And p.party = %(party)s"
			values["party"] = filters.get('party')

		if filters.get("from_date"):
			if filters.get("from_date") and filters.get("to_date"):
				conditions += " AND CAST(p.posting_date AS DATE) >= %(from_date)s  AND CAST(p.posting_date AS DATE) <= %(to_date)s"
				values["from_date"] = filters.get("from_date")
				values["to_date"] = filters.get("to_date")

			elif filters.get("from_date"):
				conditions += " AND CAST(p.posting_date AS DATE) =  %(from_date)s "
				values["from_date"] = filters.get("from_date")

		return conditions, values

