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
	return PurchaseOrderAvailREservedQth(filters).run()


class PurchaseOrderAvailREservedQth(object):
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
		if self.filters.get("item_code"):
			conditions += " AND `tabPurchase Order Item`.item_code = '%s'"%self.filters.get("item_code")
		if self.filters.get("purchase_order"):
			conditions += " AND `tabPurchase Order Item`.parent = '%s'"%self.filters.get("purchase_order")
		sql_query_new = f"""
		SELECT *,(base_qty - table1.available_qty) as reserved_qty
		FROM (
		SELECT `tabPurchase Order Item`.name as `line_name` 
		,`tabPurchase Order Item`.item_code 
		,`tabPurchase Order Item`.parent
		,`tabPurchase Order Item`.parenttype as doctype
		,`tabPurchase Order Item`.qty as `base_qty`
		,CASE
			WHEN `tabReservation Purchase Order`.reserved_qty > 0 
			then (`tabPurchase Order Item`.qty - `tabPurchase Order Item`.received_qty) - SUM(`tabReservation Purchase Order`.reserved_qty)
			else `tabPurchase Order Item`.qty - `tabPurchase Order Item`.received_qty
		end as available_qty
		from
		`tabPurchase Order Item`
		LEFT JOIN
		`tabReservation Purchase Order`
		ON `tabReservation Purchase Order`.purchase_order_line=`tabPurchase Order Item`.name 
		AND `tabReservation Purchase Order`.item=`tabPurchase Order Item`.item_code 
		LEFT JOIN
		`tabReservation`
		ON  `tabReservation Purchase Order`.parent = `tabReservation`.name 
		AND `tabReservation`.status <> "Invalid"
		WHERE {conditions}
		GROUP BY `tabPurchase Order Item`.name,`tabPurchase Order Item`.item_code
		) table1
		"""
		sql_data = frappe.db.sql(sql_query_new,as_dict=1)

		return sql_data



	def get_columns(self):
		# add columns wich appear data
		self.columns = [
			{
				"label": _("Purchase Order"),
				"fieldname": "parent",
				"fieldtype": "Link",
				"options": "Purchase Order",
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
				"fieldname": "base_qty",
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
				"fieldname": "available_qty",
				"fieldtype": "Float",
				"width": 120,
			},
	
		]


  