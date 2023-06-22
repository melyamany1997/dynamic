# Copyright (c) 2023, Dynamic and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json
from frappe import _
class EmployeePenalty(Document):
	
	@frappe.whitelist()
	def set_total_amount(self):
		pass
	
	def before_save(self):
		if self.amount <= 0:
			frappe.throw(_("Amount must be greate than '0.0' "))
	
	def on_submit(self):
		create_addtional_salary(self.name)



@frappe.whitelist()
def create_addtional_salary(source_name):
	penalty_doc = frappe.get_doc("Employee Penalty" , source_name)

	check_exist = frappe.get_list("Additional Salary",
	filters={
        'ref_docname': penalty_doc.get('name')
    },
	fields=['name']
	)
	if len(check_exist):
		frappe.throw(_("this employee penalty has addtional salary"))
	addtionall_salary_doc = frappe.new_doc('Additional Salary')
	addtionall_salary_doc.employee = penalty_doc.employee
	addtionall_salary_doc.salary_component = penalty_doc.salary_component 
	addtionall_salary_doc.payroll_date = penalty_doc.payroll_effect_date 
	addtionall_salary_doc.amount = penalty_doc.amount 
	addtionall_salary_doc.ref_doctype = "Employee Penalty"
	addtionall_salary_doc.ref_docname = penalty_doc.get('name')
	addtionall_salary_doc.overwrite_salary_structure_amount = 0
	addtionall_salary_doc.submit()




