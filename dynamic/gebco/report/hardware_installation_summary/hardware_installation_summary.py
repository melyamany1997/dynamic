# Copyright (c) 2022, Dynamic and contributors
# For license information, please see license.txt

import frappe
from frappe import _



def execute(filters=None):
	return instalation_summary(filters).run()


class instalation_summary(object):
	def __init__(self,filters=None):
		self.filters = frappe._dict(filters or {})
	
	def run(self):
		self.get_columns()
		self.get_data()
		return self.columns, self.data

	def get_columns(self):
		# add columns wich appear data
		self.columns = [
			{
				"label": _("Customer"),
				"fieldname": "customer",
				"fieldtype": "Link",
				"options": "Doctype",
				"width": 140,
			},
            {
                "fieldname": "sales_order",
                "fieldtype": "Link",
                "label": _("Sales Order"),
                "width": 150,
                "options": "Sales Order",
            },
			{
                "fieldname": "total_cars",
                "fieldtype": "Int",
                "label": _("Total Car"),
                "width": 120,
            },
			{
                "fieldname": "requested_car",
                "fieldtype": "Int",
                "label": _("requested Car"),
                "width": 120,
            },
			{
                "fieldname": "ordered_car",
                "fieldtype": "Int",
                "label": _("Ordered Car"),
                "width": 120,
            },
			{
                "fieldname": "completed_car",
                "fieldtype": "Int",
                "label": _("Completed Car"),
                "width": 120,
            },
			
        ]
		return self.columns
		
	
	def get_data(self):
		self.data = []
		self.conditions, self.values,self.query = self.get_conditions(self.filters)

		data = f"""{self.query} where {self.conditions}"""
		self.data = frappe.db.sql(data, values=self.values, as_dict=1)
		return self.data

		
	def get_conditions(self,filters):
		conditions = "1=1 "
		values = dict()
		query = ""
		dict_fields = {
			"Installation Request":['p.sales_order',"p.customer","p.total_cars","p.total_cars as `requested_car`","p.completed_cars as `completed_car`"," p.ordered_cars as `ordered_car`"],
			"Installation Order":['p.sales_order',"p.total_requested_cars as `total_cars`","p.total_cars as `ordered_car`",'p.customer','p.total_cars `requested_car`','p.completed_cars as `completed_car`'],
			"Sales Order":['p.customer','p.name as `sales_order`', 'p.total_cars as `total_cars`','p.ordered_cars as `ordered_car`','SUM(re.total_cars) as `requested_car`','SUM(re.completed_cars) as `completed_car`'],
			"default":['p.customer','p.name as `sales_order`', 'p.completed_cars as `completed_car`','p.requested_cars as `requested_car`','p.total_cars as `total_cars`','p.ordered_cars as `ordered_car`']
		}
		if filters.get("from_date"):
			if filters.get("from_date") and filters.get("to_date"):
				frappe.errprint('to_date')
				conditions += " AND date(p.creation)  >= date(%(from_date)s)  AND date(p.creation)  <= date(%(to_date)s)"
				values["from_date"] = filters.get("from_date")
				values["to_date"] = filters.get("to_date")

			if  filters.get("from_date") and not filters.get("to_date"):
				frappe.errprint(' from_date')
				conditions += " AND date(p.creation)  = date(%(from_date)s) "
				values["from_date"] = filters.get("from_date")

		#TODO:get field according to doctype
		if self.filters.get('source'):
			if self.filters.get('source') == "Installation Request":
				query_fields = self.get_query_field(dict_fields["Installation Request"])
				query = f"Select {query_fields} from `tabInstallation Request` p  "
				conditions += " AND p.name  =  %(doc_name)s "
				values["doc_name"] = filters.get("doc_name")

			if self.filters.get('source') == "Installation Order":
				query_fields = self.get_query_field(dict_fields["Installation Order"])
				query = f"Select  {query_fields} from `tabInstallation Order` p  "
				conditions += " AND p.name  =  %(doc_name)s "
				values["doc_name"] = filters.get("doc_name")

			if self.filters.get('source') == "Sales Order":
				query_fields = self.get_query_field(dict_fields["Sales Order"])
				query = f"select {query_fields} from `tabSales Order` as p JOIN `tabInstallation Request` re ON p.name = re.sales_order "
				conditions += " AND p.name  =  %(doc_name)s AND p.docstatus = 1 and re.docstatus  = 1 GROUP BY p.name"
				values["doc_name"] = filters.get("doc_name")

		if not self.filters.get('source'):
			query_fields = self.get_query_field(dict_fields["default"])
			query = f"select {query_fields} from `tabSales Order` as p"
			conditions += " AND p.docstatus = 1 "
			
		return conditions, values, query
		
	def get_query_field(self,list_field):
		fields = ''
		for field in list_field:
			fields += field + ' ,'
		return fields[:-1]

