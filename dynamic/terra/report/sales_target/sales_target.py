# Copyright (c) 2022, Dynamic and contributors
# For license information, please see license.txt



import frappe
from frappe import _
from frappe.utils import  getdate
from frappe.utils import (
	flt,
)

def execute(filters=None):
	return SalesTarget(filters).run()


class SalesTarget(object):
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
			conditions += " and sinv.creation >= '%s'"%self.filters.get("from_date")
		if self.filters.get("to_date"):
			conditions += " and sinv.creation <= '%s'"%self.filters.get("to_date")
		if self.filters.get("cost_center"):
			conditions += " and sinv.cost_center <= '%s'"%self.filters.get("cost_center")
		# if self.filters.get("branch"):
		# 	conditions += " and opport.creation <= '%s'"%self.filters.get("branch")
		# SUM(`sales_team`.`allocated_amount`)allocated_amount
		# 				,`target_details`.`target_qty`
		sql_query_new = f"""
					SELECT *,(((allocated_amount+return_amount)/target_qty)*100)`of_target`
					,(target_qty-(allocated_amount+return_amount))`of_target_amount`
					,((return_amount/target_qty)*100)return_percent
					  FROM(
						select sinv.name as sinv_name,sinv.discount_amount
						,COUNT(DISTINCT sinv.name) sinv_count
						,`sales_team`.`sales_person` as sales_person
						,COUNT(distinct sinv_items.item_code) no_items
						,SUM(sinv_items.qty) total_items_qty
						,SUM(DISTINCT sinv.grand_total) net_sales
						,(SUM(DISTINCT sinv.grand_total)/COUNT(DISTINCT sinv.name))atv
						,SUM(CASE 
							WHEN sinv.docstatus = 1 AND  sinv.status<>'Return'
							THEN `sales_team`.`allocated_amount`
							ELSE 0 
						END) AS `allocated_amount`
						,SUM(CASE 
							WHEN sinv.docstatus = 1 AND  sinv.status='Return'
							THEN `sales_team`.`allocated_amount`
							ELSE 0 
						END) AS `return_amount`
						,`target_details`.`target_qty`
						from `tabSales Invoice`sinv
						INNER JOIN `tabSales Team` sales_team
						ON sales_team.parent = sinv.name
						INNER JOIN `tabTarget Detail` target_details
						on target_details.parent=sales_team.sales_person
						INNER JOIN `tabSales Invoice Item` sinv_items
						ON sinv_items.parent=sinv.name AND sinv_items.parent=sales_team.parent
						WHERE {conditions} 
						GROUP  BY sales_team.sales_person
						)data
		""".format(conditions=conditions)
		# frappe.errprint(f"sql_query_new is ==> {sql_query_new}")
		sql_data = frappe.db.sql(sql_query_new,as_dict=1)
		# frappe.errprint(f"sql_query_new is ==> {sql_query_new}")
		return sql_data

	def get_columns(self):
		# add columns wich appear data
		self.columns = [
			# {
			# 	"label": _("Invoice"),
			# 	"fieldname": "sinv_name",
			# 	"fieldtype": "Link",
			# 	"options": "Sales Invoice",
			# 	"width": 180,
			# },
			{
				"label": _("Sales Person"),
				"fieldname": "sales_person",
				"fieldtype": "Link",
				"options": "Sales Person",
				"width": 180,
			},
			
			{
                "fieldname": "target_qty",
                "label": _("Target Qty"),
                "fieldtype": "Float",
                "width": 130,
            },
			{
                "fieldname": "allocated_amount",
                "label": _("Allocated Amount"),
                "fieldtype": "Float",
                "width": 130,
            },
			{
                "fieldname": "return_amount",
                "label": _("Return Amount"),
                "fieldtype": "Float",
                "width": 130,
            },
			{
                "fieldname": "of_target",
                "label": _("% Of Target"),
                "fieldtype": "Percent",
                "width": 130,
            },
			{
                "fieldname": "of_target_amount",
                "label": _("+/- of Target"),
                "fieldtype": "Float",
                "width": 130,
            },
			{
                "fieldname": "return_percent",
                "label": _("% Of Return"),
                "fieldtype": "Percent",
                "width": 130,
            },
			{
                "fieldname": "sinv_count",
                "label": _("No.Invoices"),
                "fieldtype": "INT",
                "width": 100,
            },
			{
                "fieldname": "no_items",
                "label": _("No.Items"),
                "fieldtype": "INT",
                "width": 100,
            },
			{
                "fieldname": "total_items_qty",
                "label": _("No.Items Qty"),
                "fieldtype": "INT",
                "width": 100,
            },
			{
                "fieldname": "net_sales",
                "label": _("Net.Sales"),
                "fieldtype": "Float",
                "width": 100,
            },
		]
