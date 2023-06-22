# Copyright (c) 2022, Dynamic and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import  getdate
from frappe.utils import (
	flt,
)

def execute(filters=None):
	return OpportuntiySourceSummary(filters).run()


class OpportuntiySourceSummary(object):
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
		item_group = ''
		if self.filters.get("from_date"):
			conditions += " and sinv_item.creation >= '%s'"%self.filters.get("from_date")
		if self.filters.get("to_date"):
			conditions += " and sinv_item.creation <= '%s'"%self.filters.get("to_date")
		if self.filters.get("cost_center"):
			conditions += " and so.cost_center = '%s'"%self.filters.get("cost_center")
		if self.filters.get("sales_person"):
			conditions += " and sales_team.sales_person = '%s'"%self.filters.get("sales_person")
		if self.filters.get("source"):
			conditions += " and Quotation.source = '%s'"%self.filters.get("source")
		sql_query_new = f"""
				SELECT so.name,Quotation.`source`,Count(so.name) total_count,sinv_item.`item_code` ,Count(so.name),SUM(so.`grand_total`) amount,so.cost_center ,
				sinv_item.`prevdoc_docname` as item_quotation,sales_person.sales_person 
				FROM `tabQuotation` as Quotation
				INNER JOIN `tabSales Order Item` sinv_item 
				ON Quotation.name=sinv_item.prevdoc_docname
				INNER JOIN `tabSales Order` so
				ON so.name=sinv_item.parent AND Quotation.name=sinv_item.prevdoc_docname
				INNER JOIN `tabSales Team` sales_person
				ON sales_person.parent=sinv_item.parent 
				WHERE {conditions}
				GROUP  BY Quotation.`source`,sales_person.`sales_person`
		""".format(conditions=conditions)
		sql_data = frappe.db.sql(sql_query_new,as_dict=1)
		# frappe.errprint(f"sql_query_new is ==> {sql_query_new}")
		return sql_data
	
	def get_columns(self):
		# add columns wich appear data
		self.columns = [
			{
				"label": _("Sales Person"),
				"fieldname": "sales_person",
				"fieldtype": "Data",
				"width": 150,
			},
			{
                "fieldname": "cost_center",
                "label": _("Cost Center"),
                "fieldtype": "Data",
                "width": 130,
            },
			{
                "fieldname": "source",
                "label": _("Source"),
                "fieldtype": "Data",
                "width": 130,
            },
			{
                "fieldname": "amount",
                "label": _("Net Sales"),
                "fieldtype": "Data",
                "width": 130,
            },
			{
                "fieldname": "total_count",
                "label": _("No.Order"),
                "fieldtype": "Data",
                "width": 130,
            },
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