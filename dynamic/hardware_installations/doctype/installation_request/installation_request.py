# Copyright (c) 2022, Dynamic and contributors
# For license information, please see license.txt

from gettext import install
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils.data import flt, nowdate


class InstallationRequest(Document):
	def validate(self):
		self.validate_qty()

	def validate_qty(self):
		if self.sales_order:
			total_cars = frappe.db.get_value("Sales Order",self.sales_order , "total_cars")
			total_requested_qty = frappe.db.sql(f"""
			select SUM(total_cars) as total_cars  from `tabInstallation Request`
			where docstatus = 1 and name <> '{self.name}' and sales_order = '{self.sales_order}'
				""", as_dict=1)
			if total_requested_qty:
				total_requested_qty = total_requested_qty[0].total_cars or 0
			else:
				total_requested_qty = 0
			if (total_cars - total_requested_qty) < self.total_cars:
				frappe.throw(_("""Sales Order {} has {}/{} car is Already Requested""").format(
					self.sales_order, total_requested_qty, flt(
						total_cars)
				))

		self.pending_cars = self.total_cars - self.completed_cars
		self.not_ordered_cars = self.total_cars - self.ordered_cars
		# frappe.throw(str(self.not_ordered_cars))


	def on_submit(self):
		if self.sales_order :
			self.update_sales_order()
	def on_cancel(self):
		if self.sales_order :
			self.update_sales_order(cancel=1)
	
	def update_sales_order(self,cancel=0):
		factor = -1 if cancel else 1
		sales_order = frappe.get_doc("Sales Order",self.sales_order)
		sales_order.requested_cars += (factor * self.total_cars)
		sales_order.not_requested_cars = sales_order.total_cars - sales_order.requested_cars
		sales_order.save()

@frappe.whitelist()
def make_installation_order(source_name):
	source = frappe.get_doc("Installation Request" , source_name)
	if source.not_ordered_cars <= 0 :
		frappe.throw(_("there is no pending cars"))
	
	installation_order = frappe.new_doc("Installation Order")
	installation_order.installation_request = source.name
	installation_order.sales_order = source.sales_order
	installation_order.posting_date = nowdate()
	
	installation_order.customer = source.customer
	installation_order.customer_name = source.customer_name
	installation_order.customer_phone_number = source.customer_phone_number
	
	installation_order.delegate = source.delegate
	installation_order.delegate_name = source.delegate_name
	installation_order.delegate_phone_number = source.delegate_phone_number


	
	installation_order.total_requested_cars = source.total_cars
	installation_order.total_cars = source.not_ordered_cars
	installation_order.notes = source.notes
	return installation_order



@frappe.whitelist()
def update_installation_request_qty(installation_request,sales_order=None):
	installation_request = frappe.get_doc("Installation Request",installation_request)
	result = frappe.db.sql(f"""
		select sum(completed_cars) as completed_qty , sum(total_cars) as total_cars from `tabInstallation Order` 
		where docstatus = 1 and  installation_request = '{installation_request.name}'
	""",as_dict=1) or 0

	completed_qty = (result[0].completed_qty or 0) if result else 0
	total_cars = (result[0].total_cars or 0) if result else 0
	
	installation_request.completed_cars = completed_qty
	installation_request.ordered_cars = total_cars
	installation_request.validate()
	installation_request.save()
	if sales_order or installation_request.sales_order :
		update_sales_order_qty(sales_order or installation_request.sales_order)




@frappe.whitelist()
def update_sales_order_qty(sales_order):
	sales_order = frappe.get_doc("Sales Order",sales_order)
	requested_cars_result = frappe.db.sql(f"""
		select sum(total_cars) as total_cars from `tabInstallation Request` 
		where docstatus = 1 and  sales_order = '{sales_order.name}'
	""",as_dict=1) or 0
	total_order_result = frappe.db.sql(f"""
		select sum(total_cars) as total_cars from `tabInstallation Order` 
		where docstatus = 1 and  sales_order = '{sales_order.name}'
	""",as_dict=1) or 0
	completed_qty_result = frappe.db.sql(f"""
		select sum(1) as completed_qty from `tabCar Installation` 
		where docstatus = 1 and  sales_order = '{sales_order.name}'
	""",as_dict=1) or 0

	completed_qty = (completed_qty_result[0].completed_qty or 0) if completed_qty_result else 0
	requested_cars = (requested_cars_result[0].total_cars or 0) if requested_cars_result else 0
	ordered_cars = (total_order_result[0].total_cars or 0) if total_order_result else 0
	
	sales_order.completed_cars = completed_qty
	sales_order.pending_cars = sales_order.total_cars - sales_order.completed_cars
	
	sales_order.ordered_cars = ordered_cars
	sales_order.not_ordered_cars = sales_order.total_cars - sales_order.ordered_cars
	
	sales_order.requested_cars = requested_cars
	sales_order.not_requested_Cars = sales_order.total_cars - sales_order.requested_cars

	sales_order.save()




	# frappe.msgprint(str(installation_request.ordered_cars))
	# frappe.msgprint(str(installation_request.ordered_cars))
	
