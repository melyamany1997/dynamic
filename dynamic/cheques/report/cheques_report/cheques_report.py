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


def execute(filters=None):
	return Cheques_report(filters).run()


class Cheques_report(object):
	def __init__(self, filters=None):
		self.filters = frappe._dict(filters or {})

	def run(self):
		self.get_columns()
		self.get_data()
		return self.columns , self.data

	def get_columns(self):
		self.columns = [
			{
			"fieldname": "Payment",
			"fieldtype": "Link",
			"label":_("Payment"),
			"options":"Payment Entry",
			"width": 150
		},
			{
			"fieldname": "Cheques NO",
			"fieldtype": "Data",
			"label": _("Cheques NO"),
			"width": 200

		},
		{
			"fieldname": "Party Type",
			"fieldtype": "Data",
			"label": _("Party Type"),
			"width": 150
		},
		{
			"fieldname": "Party",
			"fieldtype": "Data",
			"label": _("Party"),
			"width": 150
		},
		{
			"fieldname": "Cheque Status",
			"fieldtype": "Data",
			"label": _("Cheque Status"),
			"width": 200

		},
		{
			"fieldname": "Transaction Date",
			"fieldtype": "Data",
			"label": _("Transaction Date"),
			"width": 200

		},
		{
			"fieldname": "Reference Date",
			"fieldtype": "Data",
			"label": _("Reference Date"),
			"width": 200

		},
			{
			"fieldname": "Amount",
			"fieldtype": "Data",
			"label": _("Amount"),
			"width": 150
		},
		{
			"fieldname": "Bank",
			"fieldtype": "Data",
			"label": _("Bank"),
			"width": 150
		},
		{
			"fieldname": "Bank Account",
			"fieldtype": "Data",
			"label": _("Bank Account"),
			"width": 150
		},
		]

		return self.columns

	def get_data(self):
		self.data = []
		self.conditions, self.values = self.get_conditions(self.filters)
		self.data = self.get_data_from_payment_entry(self.conditions,self.values)
		return self.data

	def get_data_from_payment_entry(self,conditions = '' ,values = ''):
		query_test_p = """
		select p.name as `Payment`,p.reference_no as `Cheques NO`,p.party as `Party`,p.party_type as `Party Type`,p.cheque_status as `Cheque Status`, p.paid_amount as `Amount`,p.posting_date as `Transaction Date`,p.reference_date as `Reference Date`,p.drawn_bank as `Bank`,p.drawn_bank_account as `Bank Account` 
		from `tabPayment Entry` as p , `tabCheque` as cq
		WHERE {conditions} AND p.cheque <> '' AND p.cheque = cq.name
		""".format(conditions=conditions)
		data_dict_p = frappe.db.sql(query_test_p,values=values,as_dict=1)
		return data_dict_p

	def get_conditions(self,filters):
		conditions = "1=1 "
		values = dict()
		if filters.get("payment_type"):
			conditions += " AND p.payment_type =  %(payment_type)s "
			values["payment_type"] = filters.get("payment_type")
		if filters.get("cheque_status"):
			if filters.get("cheque_status") == 'Rejected' or filters.get("cheque_status") == "Rejected in Bank":
				conditions += " AND p.cheque_status =  %(cheque_status)s " #AND p.docstatus = '2'
			else:
				conditions += " AND p.cheque_status =  %(cheque_status)s AND p.docstatus = '1' "
			values["cheque_status"] = filters.get("cheque_status")
		if filters.get("bank"):
			conditions += " AND p.drawn_bank =  %(drawn_bank)s "
			values["drawn_bank"] = filters.get("bank")
		if filters.get("bank_account"):
			conditions += " AND p.drawn_bank_account =  %(drawn_bank_account)s "
			values["drawn_bank_account"] = filters.get("bank_account")
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