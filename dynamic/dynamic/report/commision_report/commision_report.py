# Copyright (c) 2022, Dynamic and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns, data = [], []
	columns = get_columns()
	data = get_data(filters)
	return columns, data
 



def get_columns():
	return [

		   {
			"fieldname": "invocie",
			"label": _("Sales Invoice"),
			"fieldtype": "Link",
			"options": "Sales Invoice",
		  },
		  {
			"fieldname": "sales_person",
			"label": _("Sales Person"),
			"fieldtype": "Link",
			"options": "Sales Person",
		  },
		  {
			"fieldname": "item__group",
			"label": _("Item Group"),
			"fieldtype": "Link",
			"options": "Item Group",
		  },
		  {
			"fieldname": "commission_template",
			"label": _("Commission Template"),
			"fieldtype": "Link",
			"options": "Commission Template",
		  },
		  {
			"fieldname": "base_on",
			"label": _("Based On"),
			"fieldtype": "Data",
		  },
		  {
			"fieldname": "amount",
			"label": _("Commision Amount"),
			"fieldtype": "Data",
		  },
		  {
			"fieldname": "commission_percent",
			"label": _("Commission  Percent"),
			"fieldtype": "Data",
		  },
		  {
			"fieldname": "commission_amount",
			"label": _("Commission  Amount"),
			"fieldtype": "Data",
		  },
		  {
			"fieldname": "invoice_qty",
			"label": _("Invoice Qty"),
			"fieldtype": "Data",
		  },
		  {
			"fieldname": "invocie_amount",
			"label": _("Invocie Amount"),
			"fieldtype": "Float",
		  },

	]


def get_data(filters):
	conditions = " where 1=1"
	if filters.get("sales_person"):
		conditions += " and sales_person = '%s'"%filters.get("sales_person")
	if filters.get("sales_invoice"):
		conditions += " and sales_invoice = '%s'"%filters.get("sales_invoice")
	if filters.get("item_group"):
		conditions += " and item__group = '%s'"%filters.get("item_group")
	if filters.get("from_date"):
		conditions += " and date >=date('%s')"%filters.get("from_date")
	if filters.get("to_date"):
		conditions += " and date  <= date('%s')"%filters.get("to_date")
	sql = f"""
	
	  select * from `tabSales Person Commetion`
	  {conditions}
	"""
	print(sql)
	res = frappe.db.sql(sql,as_dict=1)

	return res


