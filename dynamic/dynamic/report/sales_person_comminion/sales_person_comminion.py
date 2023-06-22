# Copyright (c) 2022, Dynamic and contributors
# For license information, please see license.txt

import frappe
from frappe import _
def get_columns(filters):

	return [
		{
            "label": _("Sales Person"),
            "fieldname": "sales_person",
            "fieldtype": "Link",
			"options":"Sales Person",
            "width": 250
        },
		{
            "label": _("Item Group"),
            "fieldname": "item_group",
            "fieldtype": "Data",
            "width": 250
        },
		{
            "label": _("amount"),
            "fieldname": "amount",
            "fieldtype": "Data",
            "width": 200
        },
		{
            "label": _("Qty"),
            "fieldname": "qty",
            "fieldtype": "Data",
            "width": 200
        },
		{
            "label": _("Incentives"),
            "fieldname": "incentives",
            "fieldtype": "Data",
            "width": 200
        },
		
		]

def get_data(filters):
	sql = """ 
		select SUM(`tabSales Invoice Item`.amount) as amount , `tabSales Invoice Item`.item_group,
		SUM(`tabSales Invoice Item`.qty) as qty , `tabSales Team`.sales_person as sales_person ,
		SUM(`tabSales Team`.incentives) as incentives
		from `tabSales Invoice`
		INNER JOIN  `tabSales Invoice Item` 
		INNER JOIN `tabSales Team`
		on `tabSales Invoice`.name = `tabSales Invoice Item`.parent
		and `tabSales Team`.parent =  `tabSales Invoice`.name
		WHERE  
		 `tabSales Invoice`.docstatus =1

	
	"""
	if filters.get("item_group") :
		item_group = filters.get("item_group")
		sql = sql + "and `tabSales Invoice Item`.item_group = '%s'"%(item_group)
	else :
		sql = sql +"and `tabSales Invoice Item`.item_group  in(SELECT name FROM `tabItem Group` WHERE is_group=0)"
	if filters.get("start_date")  and filters.get("end_date"):
		start_date = filters.get("start_date")
		end_date = filters.get("end_date")
		sql = sql + """AND `tabSales Invoice`.posting_date between '%s' and '%s'""" %(start_date ,end_date)
	if filters.get("sales_person") :
		peron = filters.get("sales_person")
		sql = sql + """AND  `tabSales Team`.sales_person ='%s' """%peron
	group_sql ="GROUP BY `tabSales Team`.sales_person , `tabSales Invoice Item`.item_group "
	fin_sql = sql + group_sql
	data = frappe.db.sql(fin_sql  ,as_dict=1)

	return data
def execute(filters=None):
	columns =  get_columns(filters)
	data = get_data(filters)
	return columns, data
