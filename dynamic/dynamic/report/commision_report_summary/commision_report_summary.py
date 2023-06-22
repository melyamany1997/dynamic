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
			"fieldname": "sales_person",
			"label": _("Sales Person"),
			"fieldtype": "Link",
			"options": "Sales Person",
			"width" :200
		  },
		  {
			"fieldname": "from_date",
			"label": _("From Date"),
			"fieldtype": "Data",
			"width" :200
		  },
		  {
			"fieldname": "to_date",
			"label": _("To Date"),
			"fieldtype": "Data",
			"width" :200
		  },  
		  {
			"fieldname": "item__group",
			"label": _("Item Group"),
			"fieldtype": "Link",
			"options": "Item Group",
			"width" :200

		  },
		  {
			"fieldname": "commission_template",
			"label": _("Commission Template"),
			"fieldtype": "Link",
			"options": "Commission Template",
			"width" :200

		  },
		  {
			"fieldname": "commission_amount",
			"label": _("Commission Amount"),
			"fieldtype": "Data",
			"width" :200

		  },
		  {
			"fieldname": "total_qty",
			"label": _("Total Qty"),
			"fieldtype": "Float",
			"width" :200

		  },
		  {
			"fieldname": "amount",
			"label": _("Total Commision"),
			"fieldtype": "Data",
			"width" :200

		  },

	]


def get_data(filters):
	conditions = " where 1=1"
	if filters.get("sales_person"):
		conditions += " and sales_person = '%s'"%filters.get("sales_person")

	data = filters.get("from_date")
	if data :
		conditions += f" and from_date >= date('{data}') "

	data = filters.get("to_date")
	if data :
		conditions += f" and to_date <= date('{data}') "

	sql = f"""
	
	  select sales_person,item__group,commission_template,commission_amount,sum(amount) as 'amount',sum(invoice_qty) as 'total_qty',from_date,to_date from `tabSales Person Commetion` 
	  {conditions}
	  group by sales_person,item__group,commission_template , from_date
	"""
	print("sql ==================> ",sql)
	res = frappe.db.sql(sql,as_dict=1)

	return res


