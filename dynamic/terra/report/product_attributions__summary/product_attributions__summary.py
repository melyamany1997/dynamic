# Copyright (c) 2022, Dynamic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import  getdate
from frappe.utils import (
	flt,
)

def execute(filters=None):
	return ProductAttributeSummary(filters).run()


class ProductAttributeSummary(object):
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
			conditions += " and sinv_item.cost_center <= '%s'"%self.filters.get("cost_center")
		if self.filters.get("sales_person"):
			conditions += " and sales_team.sales_person <= '%s'"%self.filters.get("sales_person")
		if self.filters.get("warehouse"):
			conditions += " and sinv_item.warehouse <= '%s'"%self.filters.get("warehouse")
		if self.filters.get("item_group"):
			conditions += " and sinv_item.item_group <= '%s'"%self.filters.get("item_group")
			item_group = ', "%s"'%(self.filters.get("item_group"))

		sql_query_new =  f"""
				select sales_team.sales_person ,sales_team.parent,bin.actual_qty,
				sinv_item.item_code,sinv_item.item_name,SUM(sinv_item.amount)as`Net_Sales`,SUM(sinv_item.qty)qty,COUNT(sales_team.parent)as `no.invoices`,
				sinv_item.rate,sinv_item.amount 
				,sinv_item.qty ,sinv_item.item_group,sinv_item.cost_center,sinv_item.warehouse
				from `tabSales Team` sales_team 
				INNER JOIN `tabSales Invoice` invoice
				ON invoice.name=sales_team.parent 
				INNER JOIN `tabSales Invoice Item` sinv_item 
				ON sinv_item.parent = invoice.name AND sales_team.parent=sinv_item.parent
				INNER JOIN `tabBin` bin
				ON bin.item_code=sinv_item.item_code AND sinv_item.warehouse=bin.warehouse
				WHERE {conditions}
				group BY sales_team.sales_person {item_group}
		"""
		frappe.errprint(sql_query_new)
		# sql_query_new =sql_query_new.format(conditions=conditions)
		sql_data = frappe.db.sql(sql_query_new,as_dict=1)
		return sql_data
		
	def get_previous_opportunity(self,conditions):
		if self.filters.get("from_date"):
			conditions += " and oprt.creation < '%s'"%self.filters.get("from_date")
		sql_query_new = f"""
				SELECT 'previous' as type,Count(*) as Total, 
				SUM(CASE
				WHEN oprt.status='Open' THEN 1
				ELSE 0
				END) AS pending,
				SUM(CASE
				WHEN oprt.status='Converted' THEN 1
				ELSE 0
				END) AS Converted,
				SUM(CASE
				WHEN oprt.status='Lost' THEN 1
				ELSE 0
				END) AS Lost
				FROM tabOpportunity as oprt
				LEFT JOIN tabLead as lead
				ON oprt.party_name=lead.name
				WHERE {conditions}
		""".format(conditions=conditions)
		sql_data = frappe.db.sql(sql_query_new,as_dict=1)
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
                "fieldname": "item_code",
                "label": _("Item Code"),
                "fieldtype": "Data",
                "width": 130,
            },
			{
                "fieldname": "item_name",
                "label": _("Item_Name"),
                "fieldtype": "Data",
                "width": 130,
            },
			{
                "fieldname": "Net_Sales",
                "label": _("Net Sales"),
                "fieldtype": "Data",
                "width": 130,
            },
			{
                "fieldname": "qty",
                "label": _("Qty"),
                "fieldtype": "Data",
                "width": 130,
            },
			{
                "fieldname": "no.invoices",
                "label": _("No.Inovoice"),
                "fieldtype": "Data",
                "width": 130,
            },{
                "fieldname": "actual_qty",
                "label": _("Actual Qty"),
                "fieldtype": "Data",
                "width": 130,
            },
			# {
            #     "fieldname": "balance",no.invoices
            #     "fieldtype": "Currency",
            #     "label": _("Balance"),
            #     "width": 150,
            # },
			# {
            #     "fieldname": "payment_cst",
            #     "fieldtype": "Currency",
            #     "label": _("Payment CST"),
            #     "width": 150,
            # },
			# {
            #     "fieldname": "journal_cst",
            #     "fieldtype": "Currency",
            #     "label": _("Journal CST"),
            #     "width": 150,
            # },
			# {
            #     "fieldname": "payment_supplier",
            #     "fieldtype": "Currency",
            #     "label": _("Payment Supplier"),
            #     "width": 150,
            # },
			# {
            #     "fieldname": "journal_supplier",
            #     "fieldtype": "Currency",
            #     "label": _("Journal Supplier"),
            #     "width": 150,
            # },
			# {
            #     "fieldname": "outstand",
            #     "fieldtype": "Currency",
            #     "label": _("Outstanding"),
            #     "width": 150,
            # },
			# {
            #     "fieldname": "outstand_amount",
            #     "fieldtype": "Currency",
            #     "label": _("Outstanding Amount"),
            #     "width": 150,
            # },
        ]
		return self.columns


