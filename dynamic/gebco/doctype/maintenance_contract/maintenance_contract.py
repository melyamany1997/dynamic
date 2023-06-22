# Copyright (c) 2022, Dynamic and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import date
from erpnext import get_default_company

DOMAINS = frappe.get_active_domains()
class MaintenanceContract(Document):
	def validate(self):
		if not self.remainig_visits:
			self.remainig_visits = self.number_of_visits
		self.validate_car_numbers()

	def validate_car_numbers(self):
		car_numbers = float(self.number_of_cars or 0)
		count = 0
		for car in self.cars_plate_numbers:
			if car.status == "Active":
				count +=1
		if count > float(car_numbers or 0) :
			frappe.throw(f"You Only Have {car_numbers} in contract")
	@frappe.whitelist()
	def get_customers_cars(self,customer):
		sql = f"""select name from tabCar where customer='{customer}'"""
		cars = frappe.db.sql(sql,as_dict=1)
		self.cars_plate_numbers = {}
		# self.save()
		for c in cars:
			self.append('cars_plate_numbers',{
				'plate_number':c.name,
				'status':'Active'
			})
		return True
		#self.save()
		#self.reload_doc()
		#print("carss  =>",cars)
		#self.save()
	@frappe.whitelist()
	def update_doc_status(self,*args,**kwargs):
		self.status="Completed"
		self.save()

@frappe.whitelist()
def create_sales_invoices(source_name, target_doc=None):
	doc = frappe.get_doc("Maintenance Contract",source_name)
	company_doc = frappe.get_doc("Company",get_default_company())
	sales_invoice = frappe.new_doc("Sales Invoice")
	sales_invoice.customer = doc.customer
	sales_invoice.debit_to = company_doc.default_receivable_account
	sales_invoice.maintenance_contract = doc.name
	sales_invoice.append("items",{
		"item_code":"Contract",
		"item_name":"Contract",
		"description":"Contract",
		"stock_uom":"Nos",
		"uom":"Nos",
		"qty":1,
		"rate":doc.contract_value,
		"income_account":company_doc.default_income_account,
		"cost_center":doc.cost_center
	})
	return sales_invoice
@frappe.whitelist()
def renew_contract(source_name, target_doc=None):
	doc = frappe.get_doc("Maintenance Contract", source_name)
	new_contract = frappe.new_doc("Maintenance Contract")
	new_contract.from_date  = doc.from_date
	new_contract.visits		= doc.visits
	new_contract.status = "Waiting"
	new_contract.to_date 	= doc.to_date
	new_contract.number_of_visits = doc.number_of_visits
	new_contract.customer   	  = doc.customer
	new_contract.customer_name 	  = doc.customer_name
	new_contract.contract_value   = doc.contract_value
	new_contract.guarantee 		  = doc.guarantee
	new_contract.number_of_cars   = doc.number_of_cars
	for pl in doc.cars_plate_numbers:
		new_contract.append('cars_plate_numbers',{
			"plate_number":pl.plate_number
		})
	#new_contract.save()
	return new_contract


# @frappe.whitelist()
# def get_customers_cars(customer):
# 	sql = f"""select name from tabCar where customer='{customer}'"""
# 	print("sqllllll",sql)
# 	cars = frappe.db.sql(sql,as_dict=1)
# 	for c in cars:
# 		self.append('cars_plate_numbers',{
# 			'plate_number':c.name
# 		})
# 	#print("carss  =>",cars)
# 	self.save()

@frappe.whitelist()
def update_contract_status():
	#return "asd"	
	if 'Gebco' in DOMAINS:
		sql = """select name,status,from_date ,to_date  from `tabMaintenance Contract` tmc where status !="Completed" or status is NULL  """
		res = frappe.db.sql(sql,as_dict=1)
		print(res)
		for r in res:
			try:
				doc = frappe.get_doc("Maintenance Contract",r.get("name"))
				print("1-",r.get("from_date") < date.today())
				print("2",r.get("to_date") > date.today())
				if r.get("from_date") < date.today() and r.get("to_date") > date.today():
					#doc.flags.ignore_mandatory = 1
					doc.status = "On Progress"
					doc.docstatus=1
					doc.save()
				elif r.get("to_date") < date.today():
					doc.flags.ignore_mandatory = 1
					doc.status = "Completed"
					doc.docstatus=1
					doc.save()
			except Exception as ex:
				print(str(ex))
				pass
		return True
	else:
		return False
	

