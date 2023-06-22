# Copyright (c) 2022, Dynamic and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe.utils import  getdate
from frappe.utils import (
	flt,
)

def execute(filters=None):
	return VisitsAnalysisSummary(filters).run()


class VisitsAnalysisSummary(object):
	def __init__(self,filters):
		self.filters  = frappe._dict(filters or {})
	def run(self):
		self.get_columns()
		self.get_data()
		return self.columns, self.data

	def get_data(self):
		self.data = []
		# self.conditions, self.values = self.get_conditions(self.filters)
		self.data = self.get_transaction(self.filters)
		return self.data

	def get_transaction(self,filters):
		# filter by 1-sales person 2- cost center 3- warehouse 4-item group 
		conditions = "  1=1 "
		get_new = self.get_new_opportunity(conditions)

		# frappe.errprint(f"all is ==> {get_new}")
		
		return get_new
	
	def get_new_opportunity(self,conditions):
		if self.filters.get("from_date"):
			conditions += " and Lead.creation >= '%s'"%self.filters.get("from_date")
		if self.filters.get("to_date"):
			conditions += " and Lead.creation <= '%s'"%self.filters.get("to_date")
		if self.filters.get("source"):
			conditions += " and Lead.source = '%s'"%self.filters.get("source")
		sql_query_new = f"""
				SELECT Count(Lead.`name`) total_count,Lead.`source`
				FROM `tabLead` as Lead 
				WHERE {conditions}
				GROUP  BY Lead.`source`
		""".format(conditions=conditions)
		sql_data = frappe.db.sql(sql_query_new,as_dict=1)
		# frappe.errprint(f"sql_query_new is ==> {sql_query_new}")
		return sql_data
	
	def get_columns(self):
		# add columns wich appear data
		self.columns = [
			{
				"label": _("Source"),
				"fieldname": "source",
				"fieldtype": "Data",
				"width": 150,
			},
			{
                "label": _("Total Count"),
                "fieldname": "total_count",
                "fieldtype": "Data",
                "width": 130,
            },
			# {
            #     "fieldname": "source",
            #     "label": _("Source"),
            #     "fieldtype": "Data",
            #     "width": 130,
            # },
			# {
            #     "fieldname": "amount",
            #     "label": _("Net Sales"),
            #     "fieldtype": "Data",
            #     "width": 130,
            # },
			# {
            #     "fieldname": "total_count",
            #     "label": _("No.Order"),
            #     "fieldtype": "Data",
            #     "width": 130,
            # },
			# {
            #     "fieldname": "qty",
            #     "label": _("Qty"),
            #     "fieldtype": "Data",
            #     "width": 130,
            # },
			# {
            #     "fieldname": "no.invoices",
            #     "label": _("No.Inovoice"),
            #     "fieldtype": "Data",
            #     "width": 130,
            # },
			# {
            #     "fieldname": "actual_qty",
            #     "label": _("Actual Qty"),
            #     "fieldtype": "Data",
            #     "width": 130,
            # },
		]
