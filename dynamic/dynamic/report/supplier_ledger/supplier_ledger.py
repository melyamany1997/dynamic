# Copyright (c) 2023, a and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe.utils import  getdate
from frappe.utils import (
	flt,
)

def execute(filters=None):
	return VisitPerCustomer(filters).run()


class VisitPerCustomer(object):
	def __init__(self,filters):
		self.filters  = frappe._dict(filters or {})
	def run(self):
		self.get_columns()
		self.get_data()
		return self.columns, self.data

	def get_data(self):
		self.data = []
		self.data = self.get_transaction(self.filters)
		return self.data

	def get_transaction(self,filters):
		# filter by 1-sales person 2- cost center 3- warehouse 4-item group
		conditions = "  1=1 "
		get_new = self.get_query_data(conditions)
		return get_new

	data = """
		
			"""
	def get_query_data(self,conditions):
		if self.filters.get("from_date"):
			conditions += " AND  gl.posting_date >= '%s'"%self.filters.get("from_date")
		if self.filters.get("to_date"):
			conditions += " AND  gl.posting_date <= '%s'"%self.filters.get("to_date")
		if self.filters.get("party_type"):
			conditions += " AND  gl.party_type = '%s'"%self.filters.get("party_type")
		if self.filters.get("party"):
			conditions += " AND  gl.party = '%s'"%self.filters.get("party")
		if self.filters.get("currency"):
			conditions += " AND  gl.account_currency = '%s'"%self.filters.get("currency")
		

		sql_query_new = f"""
			SELECT gl.account_currency 
			,gl.party_type
			,gl.party
			,IFNULL(
				sum(CASE 
				WHEN  gl.debit > 0 AND  gl.credit = 0  THEN gl.debit 
				WHEN  gl.credit > 0 AND  gl.debit = 0 THEN -gl.credit 
			END),0) as balance
			FROM `tabGL Entry` gl
			WHERE {conditions}
			GROUP BY gl.party 
		"""
		# frappe.errprint(f"sql_query_new is ==> {sql_query_new}")
		sql_data = frappe.db.sql(sql_query_new,as_dict=1)
		return sql_data



	def get_columns(self):
		# add columns wich appear data
		self.columns = [
			{
                "label": _("Party Type"),
                "fieldname": "party_type",
                "fieldtype": "Data",
                "width": 180,
            },
			{
                "label": _("Party"),
                "fieldname": "party",
                "fieldtype": "Data",
                "width": 180,
            },
			{
                "label": _("Balance"),
                "fieldname": "balance",
                "fieldtype": "Float",
                "width": 160,
            },
			{
                "label": _("Account Currency"),
                "fieldname": "account_currency",
                "fieldtype": "Data",
                "width": 130,
            },

		]
		
