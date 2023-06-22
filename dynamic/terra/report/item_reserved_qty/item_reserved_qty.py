# Copyright (c) 2023, Dynamic and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	return ItemReservedQty(filters).run()


class ItemReservedQty(object):
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
		# frappe.errprint(f"all is ==> {get_new}")
		return get_new

	def get_new_opportunity(self,conditions):
		if self.filters.get("from_date"):
			conditions += " and `tabReservation`.creation >= '%s'"%self.filters.get("from_date")
		if self.filters.get("to_date"):
			conditions += " and `tabReservation`.creation <= '%s'"%self.filters.get("to_date")
		if self.filters.get("item_code"):
			conditions += " and `tabBin`.item_code = '%s'"%self.filters.get("item_code")
		sql_query_new = f"""
						SELECT `tabBin`.name as 'bin'
						,`tabBin`.warehouse as 'bin_warehouse'
						,`tabBin`.item_code
						,`tabBin`.actual_qty as bin_actual_qty
						,SUM(`tabReservation Warehouse`.reserved_qty) as reserved_qty
						,(`tabBin`.actual_qty- (SUM(`tabReservation Warehouse`.reserved_qty)) ) as actual_avail_aty
						FROM `tabBin`
						LEFT JOIN `tabReservation`
						ON `tabReservation`.warehouse_source=`tabBin`.warehouse 
						AND `tabReservation`.status NOT IN ("Closed","Invalid")
						AND `tabReservation`.item_code=`tabBin`.item_code
						LEFT JOIN `tabReservation Warehouse`
						ON `tabReservation Warehouse`.parent=`tabReservation`.name 
						AND `tabReservation Warehouse`.item=`tabReservation`.item_code
						WHERE {conditions} 
						GROUP BY `tabBin`.warehouse,`tabBin`.item_code
		""".format(conditions=conditions)
		sql_data = frappe.db.sql(sql_query_new,as_dict=1)
		return sql_data

	def get_columns(self):
		# add columns wich appear data
		self.columns = [
			{
				"label": _("Warehosue"),
				"fieldname": "bin_warehouse",
				"fieldtype": "Link",
				"options": "Warehouse",
				"width": 180,
			},
			{
				"label": _("Item"),
				"fieldname": "item_code",
				"fieldtype": "Link",
				"options": "Item",
				"width": 170,
			},
			{
                "label": _("Actual QTY"),
                "fieldname": "bin_actual_qty",
                "fieldtype": "Float",
                "width": 180,
            },
			{
                "label": _("Reserved QTY"),
                "fieldname": "reserved_qty",
                "fieldtype": "Float",
                "width": 180,
            },
			{
                "label": _("Actual Avail QTY"),
                "fieldname": "actual_avail_aty",
                "fieldtype": "Float",
                "width": 180,
            },
		]
