# Copyright (c) 2022, Dynamic and contributors
# For license information, please see license.txt

from codecs import ignore_errors
from dynamic.hardware_installations.doctype.installation_request.installation_request import update_installation_request_qty, update_sales_order_qty
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils.data import flt, get_link_to_form, nowdate


class InstallationOrder(Document):
	def validate(self):
		self.set_totals()
		self.validate_qty()
		self.validate_schedule()

	def validate_qty(self):
		if self.installation_request:
			total_requested_qty = frappe.db.sql(f"""
			select SUM(total_cars) as total_cars  from `tabInstallation Order`
			where docstatus = 1 and name <> '{self.name}' and installation_request = '{self.installation_request}'
				""", as_dict=1)
			if total_requested_qty:
				total_requested_qty = total_requested_qty[0].total_cars or 0
			else:
				total_requested_qty = 0
			if (self.total_requested_cars-total_requested_qty) < self.total_cars:
				frappe.throw(_("""Request {} has {}/{} car is Already Ordered""").format(
					self.installation_request, total_requested_qty, flt(
						self.total_requested_cars)
				))

		self.pending_cars = self.total_cars - self.completed_cars

	def validate_schedule(self):
		for emp in self.installation_team_detail:
			for row in self.items:
				# sql = f"""
				# 		select ins_order.name , item.from_time , item.to_time  from `tabInstallation Order Item` item
				# 		inner join `tabInstallation Order` ins_order
				# 		on ins_order.name = item.parent
				# 		inner join `tabInstallation Team Detail` team 
				# 		on ins_order.name = team.parent
				# 		where ins_order.docstatus = 1 and team.employee = '{emp.employee}' and ins_order.name <> '{self.name}' 
				# 		and (
				# 			(from_time BETWEEN '{row.from_time}' AND '{row.to_time}') or 
				# 			(to_time BETWEEN '{row.from_time}' AND '{row.to_time}') or 
				# 			((from_time <= '{row.from_time}' ) and 
				# 			(to_time >= '{row.to_time}')) 
				# 		)
				# """
				sql = f"""
				select * from `tabEmployee Schedule` schedule 
					where schedule.docstatus = 1 and schedule .employee = '{emp.employee}'
					and schedule.installation_order <> '{self.name}'and 
					(
						(schedule.from_time BETWEEN '{row.from_time}' AND '{row.to_time}') or 
						(schedule.to_time BETWEEN '{row.from_time}' AND '{row.to_time}') or 
						((schedule.from_time <= '{row.from_time}' ) and 
						(schedule.to_time >= '{row.to_time}')) 
					)
				"""
				res = frappe.db.sql(sql, as_dict=1)
				if res and len(res) > 0:
					emp_name = emp.employee + ":" + emp.employee_name
					lnk = get_link_to_form(self.doctype, res[0].installation_order)
					frappe.msgprint(_("Invalid Schedule For Employee {} at Row {}").format(
						emp_name, row.idx
					))
					frappe.throw(_("""Employee {} has Installation Order {} from {} to {} """).format(
						emp_name, lnk, res[0].from_time, res[0].to_time
					))

	def on_submit(self):
		if self.installation_request:
			self.update_installation_request()
		
		self.create_employee_schedules()
	def on_cancel(self):
		if self.installation_request:
			self.update_installation_request(cancel=1)
		
		# self.create_employee_schedules(cancel=1)
			# update_installation_request_qty(self.installation_request)


	def create_employee_schedules (self,cancel=0) :
		for emp in self.installation_team_detail:
			for row in self.items:
				employee_schedule = frappe.new_doc("Employee Schedule")
				employee_schedule.installation_request = self.installation_request
				employee_schedule.installation_order = self.name
				employee_schedule.team = self.team
				employee_schedule.employee = emp.employee
				employee_schedule.employee_name = emp.employee_name
				employee_schedule.cars = row.cars
				employee_schedule.address = row.address
				employee_schedule.from_time = row.from_time
				employee_schedule.to_time = row.to_time
				employee_schedule.submit()



	def update_installation_request(self, cancel=0):
		installation_request = frappe.get_doc(
			"Installation Request", self.installation_request)
		factor = -1 if cancel else 1
		installation_request.ordered_cars += factor * self.total_cars
		installation_request.validate()
		installation_request.save()
		if installation_request.sales_order :
			update_sales_order_qty(installation_request.sales_order)

	# def on_update_after_submit(self):
	# 	if self.installation_request:
	# 		update_installation_request_qty(self.installation_request)

	@frappe.whitelist()
	def get_team_parties(self):
		if self.team:
			team = frappe.get_doc("Installation Team", self.team)
			self.set("installation_team_detail", [])
			for emp in team.employees:
				self.append("installation_team_detail", {
					"employee": emp.employee,
					"employee_name": emp.employee_name
				})

	@frappe.whitelist()
	def set_totals(self):
		self.total_cars = sum([(x.cars or 0)
								for x in getattr(self, "items", [])])


@frappe.whitelist()
def make_installation(source_name):
	source = frappe.get_doc("Installation Order", source_name)
	if source.pending_cars <= 0:
		frappe.throw(_("there is no pending cars"))

	installation = frappe.new_doc("Car Installation")
	installation.installation_request = source.installation_request
	installation.installation_order = source.name
	installation.sales_order = source.sales_order
	installation.installation_type = "New"
	installation.posting_date = nowdate()

	installation.customer = source.customer
	installation.customer_name = source.customer_name
	installation.customer_phone_number = source.customer_phone_number

	installation.delegate = source.delegate
	installation.delegate_name = source.delegate_name
	installation.delegate_phone_number = source.delegate_phone_number

	installation.team = source.team
	# if hasattr(installation,'installation_team_detail') :
	installation.set("installation_team_detail", [])
	for emp in source.installation_team_detail:
		# print ("emp ====> ", emp)
		installation.append("installation_team_detail", {
			"employee": emp.employee,
			"employee_name": emp.employee_name
		})

	installation.notes = source.notes
	return installation


# @frappe.whitelist()
# def update_installation_order_qty(installation_order):
# 	installation_order = frappe.get_doc("Installation Order",installation_order)
# 	result = frappe.db.sql(f"""

# 		select sum(completed_cars) as completed_qty , sum(total_cars) as total_cars from `tabInstallation Order`
# 		where docstatus = 1 and  installation_request = '{installation_request}'


# 	""",as_dict=1) or 0

# 	completed_qty = (result[0].completed_qty or 0) if result else 0
# 	total_cars = (result[0].total_cars or 0) if result else 0

# 	installation_request.completed_cars = completed_qty
# 	installation_request.ordered_cars = total_cars
# 	installation_request.validate()
# 	installation_request.save()
