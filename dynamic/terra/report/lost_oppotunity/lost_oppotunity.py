# Copyright (c) 2022, Dynamic and contributors
# For license information, please see license.txt



import frappe
from frappe import _
from frappe.utils import  getdate
from frappe.utils import (
	flt,
)

def execute(filters=None):
	return LostOpportunity(filters).run()


class LostOpportunity(object):
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
			conditions += " and opport.creation >= '%s'"%self.filters.get("from_date")
		if self.filters.get("to_date"):
			conditions += " and opport.creation <= '%s'"%self.filters.get("to_date")
		sql_query_new = f"""
						select opport.name as opp_name, opport.creation as app_creation,
						opport.order_lost_reason as lost_res,
						items.item_name, items.item_code,items.qty,items.item_group
						from `tabOpportunity`opport
						inner join `tabOpportunity Item`items
						on opport.name = items.parent
						WHERE {conditions} 
						GROUP  BY opport.name, items.item_code
	
		""".format(conditions=conditions)
		# frappe.errprint(f"sql_query_new is ==> {sql_query_new}")
		sql_data = frappe.db.sql(sql_query_new,as_dict=1)
		# frappe.errprint(f"sql_query_new is ==> {sql_data}")
		return sql_data

	def get_columns(self):
		# add columns wich appear data
		self.columns = [
			{
				"label": _("Opportunity"),
				"fieldname": "opp_name",
				"fieldtype": "Link",
				"options": "Opportunity",
				"width": 180,
			},
			{
				"label": _("Created Time"),
				"fieldname": "app_creation",
				"fieldtype": "Date",
				"width": 170,
			},
			{
                "fieldname": "item_name",
                "label": _("Name Name"),
                "fieldtype": "Data",
                "width": 130,
            },
			{
                "fieldname": "item_code",
                "label": _("Item Code"),
                "fieldtype": "Link",
				"options": "Item",
                "width": 130,
            },
			{
                "fieldname": "qty",
                "label": _("Qty"),
                "fieldtype": "Data",
                "width": 130,
            },
			{
                "fieldname": "item_group",
                "label": _("Item Group"),
                "fieldtype": "Data",
                "width": 130,
            },
			{
                "fieldname": "lost_res",
                "label": _("Lost Reason"),
                "fieldtype": "Data",
                "width": 130,
            }
		]
