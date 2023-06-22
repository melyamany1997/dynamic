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
	return opportunitiesummary(filters).run()


class opportunitiesummary(object):
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
		conditions = "  1=1 "
		if filters.get("territory"):
			conditions += " and lead.territory <= '%s'"%filters.get("territory")
		get_new = self.get_new_opportunity(conditions)
		get_previous = self.get_previous_opportunity(conditions)

		# frappe.errprint(f"all is ==> {get_new+get_previous}")
		return get_new+get_previous
	
	def get_new_opportunity(self,conditions):
		if self.filters.get("from_date"):
			conditions += " and oprt.creation >= '%s'"%self.filters.get("from_date")
		if self.filters.get("to_date"):
			conditions += " and oprt.creation <= '%s'"%self.filters.get("to_date")
		sql_query_new = f"""
				SELECT 'new' as type,COALESCE(COUNT(*), 0) as Total, 
				COALESCE(SUM(CASE
				WHEN oprt.status='Open' THEN 1
				ELSE 0
				END),0)  AS pending,
				COALESCE(SUM(CASE
				WHEN oprt.status='Converted' THEN 1
				ELSE 0
				END),0) AS Converted,
				COALESCE(SUM(CASE
				WHEN oprt.status='Lost' THEN 1
				ELSE 0
				END),0) AS Lost
				FROM tabOpportunity as oprt
				LEFT JOIN tabLead as lead
				ON oprt.party_name=lead.name
				WHERE {conditions} AND oprt.status IN ('Open','Converted','Lost')
		""".format(conditions=conditions)
		sql_data = frappe.db.sql(sql_query_new,as_dict=1)
		return sql_data
		
	def get_previous_opportunity(self,conditions):
		if self.filters.get("from_date"):
			conditions += " and oprt.creation < '%s'"%self.filters.get("from_date")
		sql_query_new = f"""
				SELECT 'previous' as type,COALESCE(COUNT(*), 0) as Total, 
				COALESCE(SUM(CASE
				WHEN oprt.status='Open' THEN 1
				ELSE 0
				END),0 )AS pending ,
				COALESCE(SUM(CASE
				WHEN oprt.status='Converted' THEN 1
				ELSE 0
				END), 0) AS Converted,
				COALESCE(SUM(CASE
				WHEN oprt.status='Lost' THEN 1
				ELSE 0
				END), 0) AS Lost
				FROM tabOpportunity as oprt
				LEFT JOIN tabLead as lead
				ON oprt.party_name=lead.name
				WHERE {conditions} AND oprt.status IN ('Open','Converted','Lost')
		""".format(conditions=conditions)
		sql_data = frappe.db.sql(sql_query_new,as_dict=1)
		return sql_data

	def get_columns(self):
		# add columns wich appear data
		self.columns = [
			{
				"label": _("Type"),
				"fieldname": "type",
				"fieldtype": "Data",
				"width": 100,
			},
			{
                "fieldname": "Total",
                "label": _("Total"),
                "fieldtype": "Data",
                "width": 100,
            },
			{
                "fieldname": "pending",
                "label": _("Pending"),
                "fieldtype": "Data",
                "width": 100,
            },
			{
                "fieldname": "Converted",
                "label": _("Converted"),
                "fieldtype": "Data",
                "width": 100,
            },
			{
                "fieldname": "Lost",
                "label": _("Lost"),
                "fieldtype": "Data",
                "width": 100,
            },
			# {
            #     "fieldname": "balance",
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


