# Copyright (c) 2023, Dynamic and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	return SalesORderReservationStatus(filters).run()


class SalesORderReservationStatus(object):
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
		conditions = "  1=1 "
		get_new = self.get_new_opportunity(conditions)
		return get_new

	def get_new_opportunity(self,conditions):
		if self.filters.get("from_date"):
			conditions += " and `tabReservation`.creation >= '%s'"%self.filters.get("from_date")
		if self.filters.get("to_date"):
			conditions += " and `tabReservation`.creation <= '%s'"%self.filters.get("to_date")
		if self.filters.get("sales_order"):
			conditions += " and `tabSales Order`.name = '%s'"%self.filters.get("sales_order")
		sql_query_new = f"""
						SELECT `tabSales Order`.name as sales_order
						,`tabReservation`.name as reservation
						,`tabReservation`.status 
						FROM `tabSales Order` 
						INNER JOIN `tabReservation`
						ON `tabReservation`.sales_order=`tabSales Order`.name
						WHERE {conditions} 
		""".format(conditions=conditions)
		sql_data = frappe.db.sql(sql_query_new,as_dict=1)
		return sql_data

	def get_columns(self):
		# add columns wich appear data
		self.columns = [
			{
				"label": _("Sales Order"),
				"fieldname": "sales_order",
				"fieldtype": "Link",
				"options": "Sales Order",
				"width": 180,
			},
			{
				"label": _("Reservation"),
				"fieldname": "reservation",
				"fieldtype": "Link",
				"options": "Reservation",
				"width": 170,
			},
			{
                "label": _("Status"),
                "fieldname": "status",
                "fieldtype": "Data",
                "width": 180,
            },
		]
