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


def execute(filters=None):
	return Cheques_summary_report(filters).run()


class Cheques_summary_report(object):
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
			"fieldname": "party_type",
			"fieldtype": "Data",
			"label": "Party Type",
			"width": 150
		},
		{
			"fieldname": "party",
			"fieldtype": "Data",
			"label": "Party",
			"width": 150
		},
		{
			"fieldname": "Total Count",
			"fieldtype": "Int",
			"label": "Total Count",
			"width": 120

		},
		]
	
		#TODO set coloms to Amount,Count
		if self.filters.get('attributes') == 'Count':
			self.columns.extend([
		{
			"fieldname": "New",
			"fieldtype": "Int",
			"label": "New",
			"width": 70
		},
		{
			"fieldname": "Paid",
			"fieldtype": "Int",
			"label": "Paid",
			"width": 70
		},
		{
			"fieldname": "Cash",
			"fieldtype": "Int",
			"label": "Cash",
			"width": 70
		},
		{
			"fieldname": "Rejected",
			"fieldtype": "Int",
			"label": "Rejected",
			"width": 90
		},
		{
			"fieldname": "Rejected in Bank",
			"fieldtype": "Int",
			"label": "Rejected in Bank",
			"width": 150
		},
		{
			"fieldname": "Collected",
			"fieldtype": "Int",
			"label": "Collected",
			"width": 100
		},
		{
			"fieldname": "Under Collect",
			"fieldtype": "Int",
			"label": "Under Collect",
			"width": 140
		},
		{
			"fieldname": "Endorsed",
			"fieldtype": "Int",
			"label": "Endorsed",
			"width": 100
		},
		{
			"fieldname": "Amount",
			"fieldtype": "Float",
			"label": "Amount",
			"width": 150
		},
			])
		if self.filters.get('attributes') == 'Amount':
			self.columns.extend([
		{
			"fieldname": "new_amount",
			"fieldtype": "Int",
			"label": "New Amount",
			"width": 120
		},
		{
			"fieldname": "paid_amount",
			"fieldtype": "Int",
			"label": "Paid Amount",
			"width": 120
		},
		{
			"fieldname": "cash_amount",
			"fieldtype": "Int",
			"label": "Cash Amount",
			"width": 120
		},
		{
			"fieldname": "rejected_amount",
			"fieldtype": "Int",
			"label": "Rejected Amount",
			"width": 140
		},
		{
			"fieldname": "rejected_bank_amount",
			"fieldtype": "Int",
			"label": "Rejected in Bank Amount",
			"width": 180
		},
		{
			"fieldname": "collected_amount",
			"fieldtype": "Int",
			"label": "Collected Amount",
			"width": 150
		},
		{
			"fieldname": "Under Collect",
			"fieldtype": "Int",
			"label": "Under Collect",
			"width": 140
		},
		{
			"fieldname": "Endorsed",
			"fieldtype": "Int",
			"label": "Endorsed",
			"width": 100
		},
		{
			"fieldname": "Amount",
			"fieldtype": "Float",
			"label": "Amount",
			"width": 150
		},
			])
		#? done for Both
		if self.filters.get('attributes') == 'Both' or self.filters.get('attributes') == None:
			self.columns.extend([
		{
			"fieldname": "New",
			"fieldtype": "Float",
			"label": "New",
			"width": 70
		},
		{
			"fieldname": "new_amount",
			"fieldtype": "Float",
			"label": "New Amount",
			"width": 120
		},
		{
			"fieldname": "Paid",
			"fieldtype": "Data",
			"label": "Paid",
			"width": 70
		},
		{
			"fieldname": "paid_amount",
			"fieldtype": "Float",
			"label": "Paid Amount",
			"width": 120
		},
		{
			"fieldname": "Cash",
			"fieldtype": "Float",
			"label": "Cash",
			"width": 70
		},
		{
			"fieldname": "cash_amount",
			"fieldtype": "Float",
			"label": "Cash Amount",
			"width": 120
		},
		{
			"fieldname": "Rejected",
			"fieldtype": "Float",
			"label": "Rejected",
			"width": 90
		},
		{
			"fieldname": "rejected_amount",
			"fieldtype": "Float",
			"label": "Rejected Amount",
			"width": 140
		},
		{
			"fieldname": "Rejected in Bank",
			"fieldtype": "Float",
			"label": "Rejected in Bank",
			"width": 150
		},
		{
			"fieldname": "rejected_bank_amount",
			"fieldtype": "Float",
			"label": "Rejected in Bank Amount",
			"width": 180
		},
		{
			"fieldname": "Collected",
			"fieldtype": "Float",
			"label": "Collected",
			"width": 100
		},
		{
			"fieldname": "collected_amount",
			"fieldtype": "Float",
			"label": "Collected Amount",
			"width": 150
		},
		{
			"fieldname": "Under Collect",
			"fieldtype": "Float",
			"label": "Under Collect",
			"width": 140
		},
		{
			"fieldname": "under_collect_amount",
			"fieldtype": "Float",
			"label": "Under Collect Amount",
			"width": 170
		},
		{
			"fieldname": "Endorsed",
			"fieldtype": "Float",
			"label": "Endorsed",
			"width": 100
		},
		{
			"fieldname": "endorsed_amount",
			"fieldtype": "Float",
			"label": "Endorsed Amount",
			"width": 170
		},
		{
			"fieldname": "Amount",
			"fieldtype": "Float",
			"label": "Amount",
			"width": 150
		},
			])
		# 	self.columns.append({
		# 	"fieldname": "posting_date",
		# 	"fieldtype": "Date",
		# 	"label": "Posting Date",
		# 	"width": 150
		# 		})
		return self.columns

	def get_data(self):
		self.data = []
		frappe.errprint(f'filters->{self.filters}')
		self.conditions, self.values = self.get_conditions(self.filters)
		self.data = self.get_data_from_payment_entry_amount(self.conditions,self.values)
		return self.data


	def get_data_from_payment_entry_amount(self,conditions = '' ,values = ''):
		query_test_p = """
		select party_type,party,count(cheque) as `Total Count`,sum(paid_amount) as Amount,
		SUM(CASE 
			WHEN cheque_status = "New" 
			THEN 1 
			ELSE 0 
		END) AS `New`,
		SUM(CASE 
			WHEN cheque_status = "New"  
			THEN paid_amount 
			ELSE 0 
		END) AS `new_amount`,
		SUM(CASE 
			WHEN cheque_status = "Rejected" 
			THEN 1 
			ELSE 0 
		END) AS `Rejected`,
		SUM(CASE 
			WHEN cheque_status = "Rejected"  
			THEN paid_amount 
			ELSE 0 
		END) AS `rejected_amount`,
		SUM(CASE 
			WHEN cheque_status = "Rejected in Bank" 
			THEN 1 
			ELSE 0 
		END) AS `Rejected in Bank`,
		SUM(CASE 
			WHEN cheque_status = "Rejected in Bank"  
			THEN paid_amount 
			ELSE 0 
		END) AS `rejected_bank_amount`,
		SUM(CASE 
			WHEN cheque_status = "Under Collect" 
			THEN 1 
			ELSE 0 
		END) AS `Under Collect Cheque`,
		SUM(CASE 
			WHEN cheque_status = "Under Collect"  
			THEN paid_amount 
			ELSE 0 
		END) AS `under_collect_amount`,
		SUM(CASE 
			WHEN cheque_status = "Collected" 
			THEN 1 
			ELSE 0 
		END) AS `Collected Cheque`,
		SUM(CASE 
			WHEN cheque_status = "Collected"  
			THEN paid_amount 
			ELSE 0 
		END) AS `collected_amount`,
		SUM(CASE 
			WHEN cheque_status = "Endorsed" 
			THEN 1 
			ELSE 0 
		END) AS `Endorsed Cheque`,
		SUM(CASE 
			WHEN cheque_status = "Endorsed"  
			THEN paid_amount 
			ELSE 0 
		END) AS `endorsed_amount`,
		SUM(CASE 
			WHEN cheque_status = "Paid" 
			THEN 1 
			ELSE 0 
		END) AS `Paid Cheque`,
		SUM(CASE 
			WHEN cheque_status = "Paid"  
			THEN paid_amount 
			ELSE 0 
		END) AS `paid_amount`,
		SUM(CASE 
			WHEN cheque_status = "Cash" 
			THEN 1 
			ELSE 0 
		END) AS `Cash Cheque`,
		SUM(CASE 
			WHEN cheque_status = "Cash"  
			THEN paid_amount 
			ELSE 0 
		END) AS `cash_amount`
		from `tabPayment Entry` p 
		WHERE {conditions} group by party
		""".format(conditions=conditions)

		data_dict_p = frappe.db.sql(query_test_p,values=values,as_dict=1)
		return data_dict_p

	def get_conditions(self,filters):
		conditions = "1=1 "
		values = dict()
		if filters.get("cheque_status"):
			if filters.get("cheque_status") == 'Rejected' or filters.get("cheque_status") == "Rejected in Bank":
				conditions += " AND p.cheque_status =  %(cheque_status)s " #AND p.docstatus = '2'
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


# def get_data_from_payment_entry(self,conditions = '' ,values = ''):
	# 	query_test_p = """
	# 	select party_type,party,count(cheque) as `Total Count`,sum(paid_amount) as Amount,
	# 	SUM(CASE 
	# 		WHEN cheque_status = "New" 
	# 		THEN 1 
	# 		ELSE 0 
	# 	END) AS `New`,
	# 	SUM(CASE 
	# 		WHEN cheque_status = "Rejected" 
	# 		THEN 1 
	# 		ELSE 0 
	# 	END) AS `Rejected`,
	# 	SUM(CASE 
	# 		WHEN cheque_status = "Rejected in Bank" 
	# 		THEN 1 
	# 		ELSE 0 
	# 	END) AS `Rejected in Bank`,
	# 	SUM(CASE 
	# 		WHEN cheque_status = "Under Collect" 
	# 		THEN 1 
	# 		ELSE 0 
	# 	END) AS `Under Collect Cheque`,
	# 	SUM(CASE 
	# 		WHEN cheque_status = "Collected" 
	# 		THEN 1 
	# 		ELSE 0 
	# 	END) AS `Collected Cheque`,
	# 	SUM(CASE 
	# 		WHEN cheque_status = "Endorsed" 
	# 		THEN 1 
	# 		ELSE 0 
	# 	END) AS `Endorsed Cheque`,
	# 	COALESCE(SUM(CASE 
	# 		WHEN cheque_status = "Paid" 
	# 		THEN 1 
	# 		ELSE 0 
	# 	END),500) AS `Paid Cheque`,
	# 	SUM(CASE 
	# 		WHEN cheque_status = "Cash" 
	# 		THEN 1 
	# 		ELSE 0 
	# 	END) AS `Cash Cheque`
	# 	from `tabPayment Entry` p 
	# 	WHERE {conditions} group by party
	# 	""".format(conditions=conditions)
	# 	data_dict_p = frappe.db.sql(query_test_p,values=values,as_dict=1)
	# return data_dict_p#

	# if 'Count' in self.filters.get('attributes'):
		# 		self.columns.extend([
		# {
		# 	"fieldname": "New",
		# 	"fieldtype": "Int",
		# 	"label": "New",
		# 	"width": 70
		# },
		# {
		# 	"fieldname": "Paid",
		# 	"fieldtype": "Int",
		# 	"label": "Paid",
		# 	"width": 70
		# },
		# {
		# 	"fieldname": "Cash",
		# 	"fieldtype": "Int",
		# 	"label": "Cash",
		# 	"width": 70
		# },
		# {
		# 	"fieldname": "Rejected",
		# 	"fieldtype": "Int",
		# 	"label": "Rejected",
		# 	"width": 90
		# },
		# {
		# 	"fieldname": "Rejected in Bank",
		# 	"fieldtype": "Int",
		# 	"label": "Rejected in Bank",
		# 	"width": 150
		# },
		# {
		# 	"fieldname": "Collected",
		# 	"fieldtype": "Int",
		# 	"label": "Collected",
		# 	"width": 100
		# },
		# {
		# 	"fieldname": "Under Collect",
		# 	"fieldtype": "Int",
		# 	"label": "Under Collect",
		# 	"width": 120
		# },
		# {
		# 	"fieldname": "Endorsed",
		# 	"fieldtype": "Int",
		# 	"label": "Endorsed",
		# 	"width": 100
		# },
		# {
		# 	"fieldname": "Amount",
		# 	"fieldtype": "Float",
		# 	"label": "Amount",
		# 	"width": 150
		# },
		# 	])