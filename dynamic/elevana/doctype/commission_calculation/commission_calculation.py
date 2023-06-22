# Copyright (c) 2023, Dynamic and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import datetime
from frappe.model.document import Document

class CommissionCalculation(Document):
	pass




@frappe.whitelist()
def calculate_commission(**kwargs):
	doc_date = kwargs.get("commission_date")
	# doc_date =  datetime.datetime.strptime(kwargs.get("commission_date"), '%Y-%m-%d') 
	# date_now= datetime.date.today()
	# # frappe.throw(f"ffget--{doc_date.date(),date_now}")
	# if(doc_date.date()==date_now):
	# 	frappe.throw("equal")
	# else:
	# 	frappe.throw("not equal")
	condition = "AND 1=1"
	if(kwargs.get("sales_person","")):
		condition += " AND sales_team.sales_person = '%s'"%(kwargs.get("sales_person",""),)

	sql = f"""
	SELECT (base.invoice_amount+base.return_invoice)total ,base.* FROM(
	SELECT invoice.posting_date,CAST(DATE_FORMAT("{doc_date}" ,'%Y-%m-01') as DATE)first_day
	,LAST_DAY("{doc_date}")last_day
	,DATE_ADD(LAST_DAY("{doc_date}"),INTERVAL 15 DAY) date_after_15
	,sales_team.sales_person,invoice.name
	,SUM(
	CASE WHEN invoice.posting_date <= LAST_DAY("{doc_date}") 
	AND invoice.posting_date >= CAST(DATE_FORMAT("{doc_date}" ,'%Y-%m-01') as DATE)
	AND invoice.is_return=0
	THEN invoice.grand_total
	ELSE 0 END) invoice_amount
	,SUM(
	CASE WHEN invoice.posting_date <= DATE_ADD(LAST_DAY("{doc_date}"),INTERVAL 15 DAY)
	AND invoice.posting_date>=CAST(DATE_FORMAT("{doc_date}" ,'%Y-%m-01') as DATE)
	AND invoice.is_return=1
	THEN (SELECT invoice.grand_total FROM `tabSales Invoice` base_inv
	WHERE base_inv.posting_date<= LAST_DAY("{doc_date}") 
	 AND base_inv.posting_date >= CAST(DATE_FORMAT("{doc_date}" ,'%Y-%m-01') as DATE)
	AND invoice.return_against=base_inv.name)
	ELSE 0 END) return_invoice
	from `tabSales Team` sales_team
	INNER JOIN `tabSales Invoice` invoice
	ON invoice.name=sales_team.parent
	WHERE invoice.docstatus=1 
	AND sales_team.sales_person NOT IN(
	SELECT demo_ledger.sales_person FROM `tabCommission Ledger` demo_ledger
	INNER JOIN `tabCommission Calculation` commission_calculation
	ON commission_calculation.name = demo_ledger.parent AND commission_calculation.docstatus=1
	WHERE  CAST(DATE_FORMAT("{doc_date}" ,'%Y-%m-01') as DATE)=CAST(DATE_FORMAT(demo_ledger.commission_date ,'%Y-%m-01') as DATE)
	)
	{condition}
	group BY sales_team.sales_person
	) base
	"""
	# frappe.errprint(sql)

	sql_date = frappe.db.sql(sql,as_dict=1)
	# frappe.errprint(sql_date)
	return get_commisio_sales_person(sql_date)

def get_commisio_sales_person(data):
	if(data):
		for row in data:
			# frappe.errprint(row)
			sql_sales_person = f"""
			SELECT ((commission_table.commission_rate/100) * {row.total}) as commission_result 
			FROM `tabCommission Template Child` commission_table
			,`tabCommission Template` template
			, `tabSales Person` sales_person
			WHERE commission_table.parent=template.name AND template.name=sales_person.commission_template
			AND sales_person.name="{row.sales_person}" 
			AND {row.total} >= commission_table.amount_from AND {row.total} < commission_table.amount_to
			"""
			data_sales_person=frappe.db.sql(sql_sales_person,as_dict=1)
			# frappe.errprint(sql_sales_person)
			# frappe.errprint(data_sales_person)
			row['incentives'] =  data_sales_person[0].commission_result if len(data_sales_person) else 0
		return data
	return data








	# sql=f"""
	# SELECT invoice.posting_date,CAST(DATE_FORMAT("{doc_date}" ,'%Y-%m-01') as DATE)first_day
	# ,LAST_DAY("{doc_date}")last_day
	# ,DATE_ADD(LAST_DAY("{doc_date}"),INTERVAL 15 DAY) date_after_15
	# ,sales_team.sales_person,invoice.name
	# ,SUM(
	# CASE WHEN invoice.posting_date <= LAST_DAY("{doc_date}")
	# AND invoice.is_return=0
	# THEN invoice.grand_total
	# ELSE 0 END) invoice_amount
	# ,SUM(
	# CASE WHEN invoice.posting_date <= DATE_ADD(LAST_DAY("{doc_date}"),INTERVAL 15 DAY)
	# AND invoice.is_return=1
	# THEN (SELECT invoice.grand_total FROM `tabSales Invoice` base_inv
	# WHERE base_inv.posting_date<= LAST_DAY("{doc_date}") 
	# AND invoice.return_against=base_inv.name)
	# ELSE 0 END) return_invoice
	# from `tabSales Team` sales_team
	# INNER JOIN `tabSales Invoice` invoice
	# ON invoice.name=sales_team.parent
	# WHERE invoice.docstatus=1 {condition}
	# group BY sales_team.sales_person
	# """