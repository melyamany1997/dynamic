# Copyright (c) 2022, Dynamic and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from datetime import date
import datetime
from frappe.utils import add_to_date
from frappe.utils import getdate
from frappe.utils import pretty_date, now, add_to_date
from erpnext.accounts.utils import get_balance_on
from operator import itemgetter
from dateutil.parser import parse
import dateutil


def execute(filters=None):
	return TotalBalance(filters).run()


class TotalBalance(object):
	def __init__(self, filters=None):
		self.filters = frappe._dict(filters or {})


	def run(self):
		self.get_columns()
		self.get_data()

		return self.columns , self.data

	def get_columns(self):
		#add columns wich appear data
		self.columns = [
			{
			"fieldname": "account",
			"label": _("Account"),
			"fieldtype": "Data",
			"width": 150
			},
			{
			"fieldname": "total_debit",
			"label": _("Total Debit"),
			"fieldtype": "Currency",
			"width": 150
			},
			{
			"fieldname": "total_credit",
			"label": _("Total Credit"),
			"fieldtype": "Currency",
			"width": 150
			},
			{
			"fieldname": "balance",
			"label": _("Balance"),
			"fieldtype": "Currency",
			"width": 150
			},
		]

		return self.columns


	def get_data(self):
		self.data = []
		self.conditions, self.values = self.get_conditions(self.filters)
		self.data = self.get_data_acc(self.conditions,self.values)

		return self.data

	def get_data_acc(self,conditions = '' ,values = ''):
		if self.filters.get("mode_of_payment"):
			mode_accounts = f"""SELECT default_account
				FROM `tabMode of Payment Account`as mpa
				where parent = '{self.filters.get("mode_of_payment")}'
				"""
			default_accounts = frappe.db.sql(mode_accounts,as_dict=1)
			if default_accounts:
				# frappe.errprint(f'default_accounts is ==>{default_accounts}')
				default_accounts_tuple= ", ".join('"'+d['default_account']+'"' for d in default_accounts)
				
				query_data = f"""
				SELECT account,total_debit,total_credit,(total_debit-total_credit) as balance
				FROM (
					SELECT account,
					SUM(CASE WHEN tge.debit > 0 THEN tge.debit ELSE 0 END) as total_debit,
					SUM(CASE WHEN tge.credit > 0 THEN tge.credit ELSE 0 END) as total_credit
					FROM `tabGL Entry` tge
					WHERE account in ({default_accounts_tuple}) AND {conditions}
					GROUP BY account
				) a """.format(conditions=conditions)
				data_dict_p = frappe.db.sql(query_data,values=values,as_dict=1)
			if not default_accounts:
				frappe.throw("Mode Of Payment Has Not Defaults Accounts")
			return data_dict_p if data_dict_p else []

	def get_conditions(self,filters):
		conditions = "1=1 "
		values = dict()
		if filters.get("from_date"):
			if filters.get("from_date") and filters.get("to_date"):
				conditions += " AND (tge.posting_date) >= %(from_date)s  AND (tge.posting_date) <= %(to_date)s"
				values["from_date"] = filters.get("from_date")
				values["to_date"] = filters.get("to_date")

			elif filters.get("from_date") and not filters.get("to_date"):
				conditions += " AND (tge.posting_date) =  %(from_date)s "
				values["from_date"] = filters.get("from_date")
		return conditions, values



#? anothrer query:
# query_data = f"""
# select account, sum(debit) total_debit,SUM(credit)total_credit from `tabGL Entry` tge
# WHERE account in ({default_accounts_tuple}) AND {conditions}
# group by account ;
# """.format(conditions=conditions)
# data_dict_p = frappe.db.sql(query_data,values=values,as_dict=1)
# for row in data_dict_p:
# 	# frappe.errprint(f"{row.get('total_debit',0)}******{row.get('total_credit',0)}")
# 	row['balance'] = row.get('total_debit',0) - row.get('total_credit',0)