# Copyright (c) 2022, Dynamic and contributors
# For license information, please see license.txt

# import frappe



import frappe
from frappe import _
from frappe.utils import  getdate
from frappe.utils import (
	flt,
)

def execute(filters=None):
	return WarehouseReservationAvailQty(filters).run()


class WarehouseReservationAvailQty(object):
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
		get_new = self.get_avail_qty(conditions)
		return get_new

	def get_avail_qty(self,conditions):
		# if self.filters.get("from_date"):
		# 	conditions += " AND `tabPurchase Invoice`.creation >= '%s'"%self.filters.get("from_date")
		# if self.filters.get("to_date"):
		# 	conditions += " AND `tabPurchase Invoice`.creation <= '%s'"%self.filters.get("to_date")
		if self.filters.get("warehouse"):
			conditions += " AND `tabBin`.warehouse = '%s'"%self.filters.get("warehouse")
		if self.filters.get("item_code"):
			conditions += " AND `tabBin`.item_code = '%s'"%self.filters.get("item_code")
		sql_query_new = f"""
		SELECT `tabBin`.warehouse
		,`tabBin`.item_code
		,`tabBin`.actual_qty
		,(`tabBin`.actual_qty-SUM(`tabReservation Warehouse`.reserved_qty))avail_qty
		,CASE 
			WHEN `tabReservation Warehouse`.reserved_qty > 0 
			then `tabBin`.actual_qty - SUM(`tabReservation Warehouse`.reserved_qty)
			ELSE `tabBin`.actual_qty 
			END as qty2
		,SUM(CASE 
			WHEN `tabReservation Warehouse`.reserved_qty > 0 
			then `tabReservation Warehouse`.reserved_qty
			ELSE 0
			END) as reserved_qty
		FROM `tabBin`
		LEFT JOIN `tabReservation Warehouse`
		ON `tabReservation Warehouse`.item=`tabBin`.item_code 
		AND `tabReservation Warehouse`.warehouse=`tabBin`.warehouse
		INNER JOIN `tabReservation`
		ON `tabReservation`.name=`tabReservation Warehouse`.parent
		AND `tabReservation`.item_code=`tabReservation Warehouse`.item
		WHERE {conditions} AND `tabReservation`.status<>'Invalid' 
		GROUP BY  `tabBin`.warehouse,`tabBin`.item_code
		"""
		sql_data = frappe.db.sql(sql_query_new,as_dict=1)

		return sql_data



	def get_columns(self):
		# add columns wich appear data
		self.columns = [
			{
				"label": _("Warehouse"),
				"fieldname": "warehouse",
				"fieldtype": "Link",
				"options": "Warehouse",
				"width": 180,
			},
			{
				"label": _("Item"),
				"fieldname": "item_code",
				"fieldtype": "Link",
				"options": "Item",
				"width": 180,
			},
			{
				"label": _("Acutal QTY"),
				"fieldname": "actual_qty",
				"fieldtype": "Float",
				"width": 180,
			},
			{
				"label": _("Reserved QTY"),
				"fieldname": "reserved_qty",
				"fieldtype": "Float",
				"width": 120,
			},
			{
				"label": _("Available QTY"),
				"fieldname": "avail_qty",
				"fieldtype": "Float",
				"width": 120,
			},
	
		]


  