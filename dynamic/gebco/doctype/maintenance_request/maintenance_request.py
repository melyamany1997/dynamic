# Copyright (c) 2022, Dynamic and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
class MaintenanceRequest(Document):
	def validate(self):
		self.validate_car_count()
		
			
			#self.save()
	def after_insert(self):
		if self.employee and self.status == "Pending":
			self.assign_request_to_employee()
			self.status = "Assined"
	def assign_request_to_employee(self):
		doc = frappe.new_doc("ToDo")
		doc.owner = self.employee
		doc.description = self.description
		doc.reference_type = "Maintenance Request"
		doc.reference_name = self.name
		doc.save()
	def validate_car_count(self):
		car_numbers = float(self.car_numbers or 0)
		table_count = 0
		if self.maintenance_contract:
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
def create_maintenance_request(source_name, target_doc=None):
	doc = frappe.get_doc("Maintenance Request",source_name)
	doc.status = "Started"
	doc.save()
	maint_temp = frappe.new_doc("Maintenance Template")
	maint_temp.maintenance_contract = doc.maintenance_contract
	maint_temp.problem = doc.description
	maint_temp.customer = doc.company_name
	maint_temp.car_numbers = doc.car_numbers
	maint_temp.maintenance_request = doc.name
	if maint_temp.maintenance_contract:
		contract = frappe.get_doc("Maintenance Contract",maint_temp.maintenance_contract)
		maint_temp.warehouse = contract.warehouse
		maint_temp.include_spare_part = contract.include_spare_parts
		for car in doc.cars:
			maint_temp.append('cars',{
				"car":car.car
			})
	else:
		for car in doc.cars_plate_numbers:
			maint_temp.append('cars_plate_numbers',{
				"plate_number":car.plate_number,
				"serial_no":car.serial_no,
				"sim_no":car.sim_no
			})

	return maint_temp
	

