import frappe


from erpnext.payroll.doctype.salary_structure_assignment.salary_structure_assignment import (
	get_assigned_salary_structure,
)

# def get_assigned_salary_structure(employee, on_date):
# 	if not employee or not on_date:
# 		return None
# 	salary_structure = frappe.db.sql(
# 		"""
# 		select name salary_structure from `tabSalary Structure Assignment`
# 		where employee=%(employee)s
# 		and docstatus = 1
# 		and %(on_date)s >= from_date order by from_date desc limit 1""",
# 		{
# 			"employee": employee,
# 			"on_date": on_date,
# 		},
# 	)
# 	return (salary_structure[0][0],salary_structure[0][1]) if salary_structure else (None,None)



# def get_employee_salary(employee, on_date):
#     pass