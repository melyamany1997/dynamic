# Copyright (c) 2022, Dynamic and contributors
# For license information, please see license.txt

from datetime import datetime
from pty import slave_open
from pydoc import doc
from shutil import ExecError
import frappe
from frappe.model.document import Document
import calendar
from frappe.utils import today
from frappe.utils.data import add_days, add_months
class SalesPersonCommetion(Document):
	def set_messing_dates(self):
		if self.date :
			#self.to_date = today
			date_list = str(self.date).split('-')
			year_name = date_list[0]
			month_name = date_list[1]
			self.from_date  = f"""{year_name}-{month_name}-01"""
			self.to_date= f"""{year_name}-{month_name}-{calendar.monthrange(int(year_name), int(month_name))[1]}"""


	#caculate item group qty / amount in range from date to to date values	
	def caculate_qty_amount(self):
		if self.date :
			caculation_sql =  frappe.db.sql( f""" SELECT 
								SUM(`tabSales Invoice Item`.amount) as amount ,
								SUM(`tabSales Invoice Item`.qty) as qty
								FROM 
								`tabSales Invoice` INNER JOIN 
								`tabSales Invoice Item`
								ON `tabSales Invoice`.name = `tabSales Invoice Item`.parent
								WHERE `tabSales Invoice`.name in 
								(SELECT parent FROM `tabSales Team` 
								WHERE sales_person = '{self.sales_person}')
								AND `tabSales Invoice`.docstatus = 1 and
								`tabSales Invoice Item`.item_group = '{self.item__group}' and 
								`tabSales Invoice`.posting_date between '{self.from_date }'
								and '{self.to_date}' 
							""" ,as_dict =1)
			
			if caculation_sql and len (caculation_sql) > 0 :
				total_amount =  float(caculation_sql[0].get("amount") or 0) + float(self.invocie_amount or 0)
				totat_qty = float(caculation_sql[0].get("qty") or 0) + float(self.invoice_qty or 0 )
				amount = total_amount if self.base_on == "Amount" else totat_qty
				template_rate =frappe.db.sql(f""" 
				SELECT commission_amount as amount , commission_rate as rate 
				FROM `tabCommission Template Child` WHERE parent = '{self.commission_template}'
				AND amount_from < {amount}
				""",as_dict =1)
				if template_rate and len(template_rate) > 0 :
					self.commission_percent = max([float(x.get('rate') or 0)  for x in template_rate])
					self.commission_amount  = max([float(x.get('amount') or 0)for x in template_rate])
				percent_factor = self.invoice_qty if self.base_on == "Qty" else  self.invocie_amount
				main_amount = float(self.commission_amount or 0) if float(self.commission_amount or 0)> 0 else float(self.commission_percent or 0)  *percent_factor 
				if self.base_on == "Qty":
					if float(self.commission_amount or 0) > 0:
						main_amount = float(main_amount or 0) * float(self.invoice_qty or 0)
					else:
						main_amount = float(self.invocie_amount or 0) * float(self.invoice_qty or 0) * float(self.commission_percent or 0) / 100



				self.amount = main_amount
	#update monyhlu commetion base on date and item group 
	def update_monthly_commetions(self):
		try:
			if float(self.amount) > 0:
				# update_sql =  f"""
				# update `tabSales Person Commetion` 
				# set amount      =  {self.amount} 
				# ,commission_percent = {self.commission_percent}
				# ,commission_amount  = {self.commission_amount}
				# where
				# sales_person            = '{self.sales_person}'
				# and item__group         = '{self.item__group}'
				# and from_date           = '{self.from_date}'
				# and to_date             = '{self.to_date}'
				# and commission_template = '{self.commission_template}'
				# """

				# frappe.db.sql(update_sql)
				# frappe.db.commit()
				docs = frappe.get_list("Sales Person Commetion",{
					"sales_person":self.sales_person,
					"item__group":self.item__group,
					"from_date":self.from_date,
					"to_date":self.to_date,
				})
				for d in docs:
					doc = frappe.get_doc("Sales Person Commetion",d.name)
					re_result = self.re_caculate_qty_amount(doc)
					sql = """ update `tabSales Person Commetion` set amount={},commission_amount={},
					commission_percent={}  where name ='{}'""".format(re_result,self.commission_amount,self.commission_percent,d.name)
					frappe.db.sql(sql)
					frappe.db.commit()

		except Exception as ex:
			print("from exception errror  ==================> ",str(ex))
			error = frappe.new_doc("Error Log")
			error.method = f"update_monthly_commetions while save {self.name}"
			error.error = str(ex)
			error.save() 
		

	# def validate_invocie_status(self):
	# 		# invocie = frappe.get_doc("Sales Invoice" , self.invocie).docstatus
	# 		# if invocie == 1 :
	# 		self.update_monthly_commetions()
		
	def validate(self):
		self.set_messing_dates()
		self.caculate_qty_amount()
		self.update_monthly_commetions()
		
	
	def remove_raw(self) :
		frappe.throw("Remove")

	def re_caculate_qty_amount(self,doc):
		if doc.date :
			caculation_sql =  frappe.db.sql( f""" SELECT 
								SUM(`tabSales Invoice Item`.amount) as amount ,
								SUM(`tabSales Invoice Item`.qty) as qty
								FROM 
								`tabSales Invoice` INNER JOIN 
								`tabSales Invoice Item`
								ON `tabSales Invoice`.name = `tabSales Invoice Item`.parent
								WHERE `tabSales Invoice`.name in 
								(SELECT parent FROM `tabSales Team` 
								WHERE sales_person = '{doc.sales_person}')
								AND `tabSales Invoice`.docstatus = 1 and
								`tabSales Invoice Item`.item_group = '{doc.item__group}' and 
								`tabSales Invoice`.posting_date between '{doc.from_date }'
								and '{doc.to_date}' 
							""" ,as_dict =1)
			
			if caculation_sql and len (caculation_sql) > 0 :
				total_amount =  float(caculation_sql[0].get("amount") or 0) + float(doc.invocie_amount or 0)
				totat_qty = float(caculation_sql[0].get("qty") or 0) + float(doc.invoice_qty or 0 )
				amount = total_amount if doc.base_on == "Amount" else totat_qty
				template_rate =frappe.db.sql(f""" 
				SELECT commission_amount as amount , commission_rate as rate 
				FROM `tabCommission Template Child` WHERE parent = '{doc.commission_template}'
				AND amount_from < {amount}
				""",as_dict =1)
				if template_rate and len(template_rate) > 0 :
					doc.commission_percent = max([float(x.get('rate') or 0)  for x in template_rate])
					doc.commission_amount  = max([float(x.get('amount') or 0)for x in template_rate])
				percent_factor = doc.invoice_qty if doc.base_on == "Qty" else  doc.invocie_amount
				main_amount = float(self.commission_amount or 0) if float(self.commission_amount or 0)> 0 else float(self.commission_percent or 0)  *percent_factor 
				if doc.base_on == "Qty":
					if float(self.commission_amount or 0) > 0:
						main_amount = float(main_amount or 0) * float(doc.invoice_qty or 0)
					else:
						main_amount = float(doc.invocie_amount or 0) * float(doc.invoice_qty or 0) * float(self.commission_percent or 0) / 100


				#print("main amount------------------------------ ",main_amount,doc.name)
				return main_amount
		return 0




@frappe.whitelist()
def update_month_previous_logs():
	first_day = datetime.today().replace(day=1)
	last_day = add_days(add_months(first_day, 1),-1) 

	sql = f"""
				select
					name ,
					sales_person ,
					item__group ,
					commission_template ,
					commission_amount ,
					invoice_qty ,
					from_date ,
					to_date
				from
					`tabSales Person Commetion` t1
				where
					t1.name = (
					select
						t2.name
					from
						`tabSales Person Commetion` t2
					where
						t2.from_date = date('{first_day}')
						and t2.to_date = date('{last_day}')
						and t1.sales_person = t2.sales_person
						and t1.item__group = t2.item__group
						and t1.commission_template = t2.commission_template
					ORDER BY
						t2.sales_person ,
						t2.item__group ,
						t2.commission_template ,
						t2.creation DESC
					limit 1
				)
				ORDER BY
					t1.sales_person ,
					t1.item__group ,
					t1.commission_template ,
					t1.creation DESC
	"""
	logs = frappe.db.sql(sql,as_dict=1) or []

	for row in logs :
		doc = frappe.get_doc("Sales Person Commetion" , row.name)
		doc.save()



@frappe.whitelist()
def update_month_previous_logs_for_person(first_day , last_day , item_group , person ):

	sql = f"""
				select
					name ,
					sales_person ,
					item__group ,
					commission_template ,
					commission_amount ,
					invoice_qty ,
					from_date ,
					to_date
				from
					`tabSales Person Commetion` t1
				where
					t1.name = (
					select
						t2.name
					from
						`tabSales Person Commetion` t2
					where
						t2.from_date = date('{first_day}')
						and t1.sales_person ='{person}' and t1.item__group ='{item_group}'
						and t2.to_date = date('{last_day}')
						and t1.sales_person = t2.sales_person
						and t1.item__group = t2.item__group
						and t1.commission_template = t2.commission_template
					ORDER BY
						t2.sales_person ,
						t2.item__group ,
						t2.commission_template ,
						t2.creation DESC
					limit 1
				)
				ORDER BY
					t1.sales_person ,
					t1.item__group ,
					t1.commission_template ,
					t1.creation DESC
	"""
	logs = frappe.db.sql(sql,as_dict=1) or []

	for row in logs :
		doc = frappe.get_doc("Sales Person Commetion" , row.name)
		doc.save()
