# Copyright (c) 2022, Dynamic and contributors
# For license information, please see license.txt



import frappe
from frappe import _
from frappe.utils import  getdate
from frappe.utils import (
	flt,
)

def execute(filters=None):
	return ActivitiesSummary(filters).run()


class ActivitiesSummary(object):
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
			conditions += " and active.creation >= '%s'"%self.filters.get("from_date")
		if self.filters.get("to_date"):
			conditions += " and active.creation <= '%s'"%self.filters.get("to_date")
		if self.filters.get("source"):
			conditions += " and active.local_source <= '%s'"%self.filters.get("source")
		if self.filters.get("branch"):
			conditions += " and active.branch <= '%s'"%self.filters.get("branch")
		sql_query_new = f"""
						select active.name as activity, active.type, active.local_source, active.branch,
						active.customer,active.creation,active.phone_no
						from `tabActions`active
						WHERE {conditions} 
						GROUP  BY active.name
		""".format(conditions=conditions)
		sql_data = frappe.db.sql(sql_query_new,as_dict=1)
		return sql_data

	def get_columns(self):
		# add columns wich appear data
		self.columns = [
			{
				"label": _("Activity"),
				"fieldname": "activity",
				"fieldtype": "Link",
				"options": "Activities",
				"width": 180,
			},
			{
				"label": _("Created Time"),
				"fieldname": "creation",
				"fieldtype": "Date",
				"width": 170,
			},
			{
                "fieldname": "type",
                "label": _("Type"),
                "fieldtype": "Data",
                "width": 130,
            },
			{
                "fieldname": "local_source",
                "label": _("Source"),
                "fieldtype": "Data",
                "width": 130,
            },
			{
                "fieldname": "branch",
                "label": _("Branch"),
                "fieldtype": "Data",
                "width": 130,
            },
			{
                "fieldname": "customer",
                "label": _("Customer"),
                "fieldtype": "Link",
				"options": "Customer",
                "width": 130,
            },
			{
                "fieldname": "phone_no",
                "label": _("Phone.no"),
                "fieldtype": "Data",
                "width": 130,
            },
			{
                "fieldname": "notes",
                "label": _("Notes"),
                "fieldtype": "Data",
                "width": 130,
            }
		]
