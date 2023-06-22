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
	return PayInvoicePerOrder(filters).run()


class PayInvoicePerOrder(object):
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
		get_new = self.get_all_data(conditions)
		return get_new

	def get_all_data(self,conditions):
		if self.filters.get("from_date"):
			conditions += " AND `tabPurchase Invoice`.creation >= '%s'"%self.filters.get("from_date")
		if self.filters.get("to_date"):
			conditions += " AND `tabPurchase Invoice`.creation <= '%s'"%self.filters.get("to_date")
		sql_query_new = f"""
		SELECT DISTINCT `tabPayment Entry Reference`.parent payment_entry
		,`tabPurchase Invoice Item`.parent purchase_invoice
		,`tabPurchase Order`.name purchase_order
		,`tabPayment Entry Reference`.reference_doctype
		,`tabPayment Entry Reference`.reference_name
		,`tabPayment Entry Reference`.allocated_amount 
		,`tabPurchase Order`.grand_total po_order_amount
		,`tabPurchase Invoice`.grand_total pi_invoice_amount
		,`tabPayment Entry`.paid_amount
		,`tabPayment Entry`.unallocated_amount
		,`tabPayment Entry`.total_allocated_amount
		FROM `tabPurchase Invoice Item`
		INNER JOIN `tabPurchase Order`
		ON `tabPurchase Invoice Item`.purchase_order=`tabPurchase Order`.name
		INNER JOIN `tabPayment Entry Reference`
		ON 
		(`tabPayment Entry Reference`.reference_doctype IN('Purchase Invoice','Purchase Order')
		AND `tabPayment Entry Reference`.reference_name IN (`tabPurchase Order`.name,`tabPurchase Invoice Item`.parent)
		)
		INNER JOIN `tabPurchase Invoice` 
		ON`tabPurchase Invoice Item`.parent=`tabPurchase Invoice`.name
		INNER JOIN `tabPayment Entry` 
		ON `tabPayment Entry`.name=`tabPayment Entry Reference`.parent
		WHERE  {conditions} AND `tabPayment Entry Reference`.reference_doctype IN('Purchase Invoice','Purchase Order')
		AND `tabPurchase Invoice`.docstatus<>2 
		"""
		sql_data = frappe.db.sql(sql_query_new,as_dict=1)

		return sql_data



	def get_columns(self):
		# add columns wich appear data
		self.columns = [
			{
				"label": _("Purchase Order"),
				"fieldname": "purchase_order",
				"fieldtype": "Link",
				"options": "Purchase Order",
				"width": 180,
			},
			{
				"label": _("Purchase Invoice"),
				"fieldname": "purchase_invoice",
				"fieldtype": "Link",
				"options": "Purchase Invoice",
				"width": 180,
			},
			{
				"label": _("Payment Entry"),
				"fieldname": "payment_entry",
				"fieldtype": "Link",
				"options": "Payment Entry",
				"width": 180,
			},
			{
				"label": _("Purchase Order Grand Total"),
				"fieldname": "po_order_amount",
				"fieldtype": "Currency",
				"width": 120,
			},
			{
				"label": _("Purchase Invoice Grand Total"),
				"fieldname": "pi_invoice_amount",
				"fieldtype": "Currency",
				"width": 120,
			},
			{
				"label": _("Paid Amount"),
				"fieldname": "paid_amount",
				"fieldtype": "Currency",
				"width": 120,
			},
			{
				"label": _("Unallocated Amount"),
				"fieldname": "unallocated_amount",
				"fieldtype": "Currency",
				"width": 120,
			},
			{
				"label": _("Total Allocated Amount"),
				"fieldname": "total_allocated_amount",
				"fieldtype": "Currency",
				"width": 120,
			},
	
		]


  