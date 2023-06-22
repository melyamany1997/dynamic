# Copyright (c) 2022, Dynamic and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from erpnext import get_default_company
from frappe import _

class MaintenanceTemplate(Document):
	def validate(self):
		self.validate_car_numbers()
		self.validate_car_count()
	def on_submit(self):
		self.update_contract_visits()
	def validate_car_numbers(self):
		un_existing_list = []
		if self.maintenance_contract and len(self.maintenance_contract) > 2:
			contract = frappe.get_doc("Maintenance Contract",self.maintenance_contract)
			for pnumber in self.cars_plate_numbers:
				exist=False
				for p_number in contract.cars_plate_numbers:
					if p_number.plate_number == pnumber.plate_number:
						exist = True
				if not exist:
					un_existing_list.append(str(pnumber.plate_number))
		if len(un_existing_list) > 0:
			error_str = "".join(un_existing_list)
			frappe.throw(_(f"This Plate Number doesnt exist in contract {error_str}"))

	def validate_car_count(self):
		car_numbers = float(self.car_numbers or 0)
		table_count = 0
		if self.maintenance_contract and len(self.maintenance_contract) > 2:
			contract = frappe.get_doc("Maintenance Contract",self.maintenance_contract)
			car_count_from_contract = contract.number_of_cars
			if car_numbers > car_count_from_contract :
				frappe.throw(_(f"You Only Have {car_count_from_contract} In Contract"))
		if self.maintenance_contract:
			for car in self.cars :
				table_count +=1
		else:
			for car in self.cars_plate_numbers:
				table_count +=1
		if table_count > car_numbers:
			frappe.throw(_(f"You Only Have {car_numbers}"))
	@frappe.whitelist()
	def create_stock_entrys(self):
		try:
			doc = frappe.new_doc("Stock Entry")
			doc.stock_entry_type = "Material Issue"
			doc.company          = get_default_company()
			doc.maintenance_template = self.name
			#doc.save()
			for item in self.items:
				doc.append('items',{
					"s_warehouse": self.warehouse,
					"item_code":item.item,
					"item_name":item.item_name,
					"qty":item.qty,
					"stock_uom":item.uom,
					"basic_rate":item.price
				})
			doc.save()
			doc.docstatus=1
			doc.save()
			self.stock_entry = doc.name
			self.save()
			frappe.msgprint("Stock Entry Created Successfully")
		except Exception as ex:
			frappe.msgprint(str(ex))

	@frappe.whitelist()
	def get_item_price(self,item_code):
		sql = f"""
			select price_list_rate FROM `tabItem Price` tip where item_code ='{item_code}' and price_list='Standard Selling' limit 1
		"""
		print("sql ========>",sql)
		result = frappe.db.sql(sql,as_dict=1)
		print("result ======>",result)
		if len(result) > 0:
			return result[0].price_list_rate
		else:
			return 0

	@frappe.whitelist()
	def update_contract_visits(self):
		if self.maintenance_contract:
			contract = frappe.get_doc("Maintenance Contract",self.maintenance_contract)
			if contract.visits == "Limited" :
				total_visits = float(contract.number_of_visits or 0)
				#print("aaaaaasddddddddddddddddddfggggggggg==============",contract.remainig_visits)
				if float(contract.completed_visits or 0) < total_visits: 
					contract.completed_visits = float(contract.completed_visits or 0) + 1
					contract.remainig_visits = float(contract.remainig_visits or 0) -1 
					contract.save()
				else:
					frappe.throw(f"This Customer Completed his {total_visits} visits")
		else:
			pass
	
	@frappe.whitelist()
	def check_cars_from_contract(self,car):
		contract = frappe.get_doc("Maintenance Contract",self.maintenance_contract)
		cars    = contract.cars_plate_numbers
		#exist = False
		for c in cars:
			if c.plate_number == car :
				return {"exist":True}
		#print("exist =>",exist)
		return {"exist":False} 
	
@frappe.whitelist()
def create_delivery_note(source_name, target_doc=None):
	doc = frappe.get_doc("Maintenance Template" , source_name)
	if doc.status == "Waiting":
		doc.status = "On Progress"
		doc.save()
	delivery_note = frappe.new_doc("Delivery Note")
	delivery_note.company = get_default_company()
	delivery_note.customer = doc.customer
	delivery_note.maintenance_template = source_name
	# if doc.sales_invoice:
	# 	delivery_note.per_billed =100
	for item in doc.items:
		delivery_note.append('items',
			{
				"item_code": item.item,
				"item_name":item.item_name,
				"description":item.item_name,
				"qty":item.qty,
				"stock_uom":item.uom,
				"uom":item.uom,
				"warehouse": doc.warehouse,
				"rate": item.price,
				"against_sales_invoice":doc.sales_invoice
			}
		)
	# for item in doc.service_items:
	# 	delivery_note.append('items',
	# 		{
	# 			"item_code": item.item,
	# 			"item_name":item.item_name,
	# 			"description":item.description,
	# 			"qty":item.qty,
	# 			"stock_uom":item.uom,
	# 			"uom":item.uom,
	# 			"warehouse": doc.warehouse,
	# 			"rate": item.price
	# 		}
	# 	)
	return delivery_note


@frappe.whitelist()
def create_sales_invoice(source_name, target_doc=None):
	doc = frappe.get_doc("Maintenance Template" , source_name)
	if doc.status == "Waiting":
		doc.status = "On Progress"
		doc.save()
	company_doc = frappe.get_doc("Company",get_default_company()) 
	sales_invoice = frappe.new_doc("Sales Invoice")
	sales_invoice.company = get_default_company()
	sales_invoice.customer = doc.customer
	sales_invoice.debit_to = company_doc.default_receivable_account
	sales_invoice.maintenance_template = source_name
	for item in doc.items:
		sales_invoice.append('items',
			{
				"item_code": item.item,
				"item_name":item.item_name,
				"description":item.item_name,
				"qty":item.qty,
				"stock_uom":item.uom,
				"uom":item.uom,
				"warehouse": doc.warehouse,
				"rate": item.price,
				"income_account":company_doc.default_income_account,
				"cost_center":doc.cost_center
			}
		)
	for item in doc.service_items:
		sales_invoice.append('items',
			{
				"item_code": item.item,
				"item_name":item.item_name,
				"description":item.description,
				"qty":item.qty,
				"stock_uom":item.uom,
				"uom":item.uom,
				"warehouse": doc.warehouse,
				"rate": item.price,
				"income_account":company_doc.default_income_account,
				"cost_center":doc.cost_center
			}
		)
	return sales_invoice


				
