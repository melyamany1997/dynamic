# Copyright (c) 2023, Dynamic AND contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	return GroosProfitInvoice(filters).run()


class GroosProfitInvoice(object):
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
		conditions = self.get_conditions()
		self.get_invoices_items(conditions)
		# frappe.errprint(f"self.invoices is ==> {self.invoices}")
		# frappe.errprint(f"self.returned_invoices is ==> {self.returned_invoices}")
		return self.invoices

	def get_conditions(self):
		conditions = "  1=1 "
		if self.filters.get("from_date"):
			conditions += " AND `si`.creation >= '%s'"%self.filters.get("from_date")
		if self.filters.get("to_date"):
			conditions += " AND `si`.creation <= '%s'"%self.filters.get("to_date")
		return conditions

	def get_invoices_items(self,conditions):
		sql_query_new = f"""
				SELECT tab1.*,(tab1.total_paid_amount+tab1.total_return_amount) as total_net_sales_amount
				,(tab1.total_paid_qty+tab1.total_return_qty) as total_net_slaes_qty
				FROM (
				select si.name, si_item.item_code, si_item.stock_qty as qty
				, si_item.base_net_amount as base_amount
				,SUM(
					CASE WHEN si.docstatus = 1 AND si.is_return = 0 THEN si_item.base_net_amount  ELSE 0 END
					)total_paid_amount
				,SUM(
					CASE WHEN si.docstatus = 1 AND si.is_return = 0 THEN  si_item.stock_qty ELSE 0 END
					)total_paid_qty
				,SUM(
					CASE WHEN si.docstatus = 1 AND si.is_return = 1 THEN si_item.base_net_amount  ELSE 0 END
					)total_return_amount
				,SUM(
					CASE WHEN si.docstatus = 1 AND si.is_return = 1 THEN si_item.stock_qty  ELSE 0 END
					)total_return_qty
				from
					`tabSales Invoice` si, `tabSales Invoice Item` si_item
				where
					si.name = si_item.parent
					AND si.docstatus = 1
					AND {conditions}
				GROUP BY si_item.item_code
				) tab1
		"""

		self.invoices =  frappe.db.sql(sql_query_new,as_dict=1)
	


	def get_columns(self):
		# add columns wich appear data
		self.columns = [
			{
				"label": _("Item"),
				"fieldname": "item_code",
				"fieldtype": "Link",
				"options": "Item",
				"width": 170,
			},
			{
				"label": _("Total Selling Amount"),
				"fieldname": "total_paid_amount",
				"fieldtype": "Currency",
				"width": 180,
			},
			{
				"label": _("Total Selling QTY"),
				"fieldname": "total_paid_qty",
				"fieldtype": "Float",
				"width": 180,
			},
			{
				"label": _("Total Return Amount"),
				"fieldname": "total_return_amount",
				"fieldtype": "Currency",
				"width": 180,
			},
			{
				"label": _("Total Return QTY"),
				"fieldname": "total_return_qty",
				"fieldtype": "Float",
				"width": 180,
			},
			{
				"label": _("Total Net Sales Amount"),
				"fieldname": "total_net_sales_amount",
				"fieldtype": "Currency",
				"width": 180,
			},
			{
				"label": _("Total Net Sales QTY"),
				"fieldname": "total_net_slaes_qty",
				"fieldtype": "Float",
				"width": 180,
			},
			
			
		]
