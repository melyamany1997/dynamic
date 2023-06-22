# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from datetime import datetime,timedelta

class Permission(Document):

	def validate(self):
		department=[]
		department=frappe.db.sql("""select department from tabEmployee where name='{}'""".format(self.employee),as_dict=1)
		asd=department[0].get('department')
		#frappe.msgprint(asd)
		if not asd:
			frappe.throw(_("employee doesn't has department"))
		employee = frappe.get_doc("Employee",self.employee)
		if not employee.attendance_rule :
			frappe.throw(_("employee doesn't has Attendance Rule"))
		attendance_role = frappe.get_doc("Attendance Rule",employee.attendance_rule)
		if not attendance_role.max_permissions_count :
			frappe.throw(_("Employee {} doesn't have any Permission in Attendance Rule \n Please Set Max Permission Count in Attendance Rule {}".format(self.employee,employee.attendance_rule)))
		if not attendance_role.max_permission_minutes:
			frappe.throw(_("Employee {} doesn't have any Permission in Attendance Rule \n Please Set Max Permission Minutes in Attendance Rule {}".format(self.employee,employee.attendance_rule)))
		if not attendance_role.max_permission_minute_per_once:
			frappe.throw(_("Employee {} doesn't have any Permission in Attendance Rule \n Please Set Max Permission Minutes Per Once in Attendance Rule {}".format(self.employee, employee.attendance_rule)))

		payroll_month = frappe.db.sql("""
		select * from `tabPayroll Period` where is_closed = 0 and docstatus < 2 and attendance_start_date <= '{date}' and attendance_end_date >= '{date}'  order by modified desc limit 1
		""".format(date = self.date),as_dict=1)
		# frappe.msgprint('str(payroll_month)')
		# frappe.msgprint(str(payroll_month))
		# frappe.msgprint(str(self.date))
		if not payroll_month:
			frappe.throw(_("Payroll Period is Closed or doesn't Created to this period "))
		payroll_month = payroll_month [0]
		# sql= """select Count(*) as total_count ,
		# 			ifnull(SUM((TIME_TO_SEC(SUBTIME( ifnull(to_time,TIME_TO_SEC('00:00:00')), ifnull(from_time,TIME_TO_SEC('00:00:00')))) /60)),0) as total_min
		# 			from tabPermission where employee = '{employee}'
		# 			and date(date) between date('{start_date}')  and date('{end_date}')
		# 			and docstatus = 1 and status = 'Completed'
		# 			and name <> '{name}'
		# 			""".format(name=self.name,employee=self.employee, start_date=payroll_month.start_date , end_date = payroll_month.end_date)
		# frappe.msgprint(sql)
		perviuos_permission = frappe.db.sql("""select Count(*) as total_count ,  
					ifnull(SUM((TIME_TO_SEC(SUBTIME( ifnull(to_time,TIME_TO_SEC('00:00:00')), ifnull(from_time,TIME_TO_SEC('00:00:00')))) /60)),0) as total_min 
					from tabPermission where employee = '{employee}' 
					and date(date) between date('{start_date}')  and date('{end_date}') 
					and docstatus = 1 and status = 'Completed'
					and name <> '{name}'
					""".format(name=self.name,employee=self.employee, start_date=payroll_month.attendance_start_date , end_date = payroll_month.attendance_end_date),as_dict=1)
		from_time = datetime.strptime(self.from_time , "%H:%M:%S")
		to_time = datetime.strptime(self.to_time , "%H:%M:%S")
		duration = float((to_time - from_time).seconds)/60
		# frappe.msgprint('str(perviuos_permission[0].total_count )')
		# frappe.msgprint(str(perviuos_permission[0].total_count))
		# frappe.msgprint('str(attendance_role.max_permissions_count)')
		# frappe.msgprint(str(attendance_role.max_permissions_count))
		if perviuos_permission[0].total_count >= attendance_role.max_permissions_count :
			frappe.throw(_("Employee {} exceed the max Permission Times \n Please Set Max Permission Count in Attendance Rule {}".format(self.employee,employee.attendance_rule)))
		# frappe.msgprint('str(perviuos_permission[0].total_min )')
		# frappe.msgprint(str(perviuos_permission[0].total_min))
		# frappe.msgprint('str(duration)')
		# frappe.msgprint(str(duration))
		# frappe.msgprint(str(perviuos_permission[0].total_min + duration))
		# frappe.msgprint(str(perviuos_permission[0].total_min + duration))
		# frappe.msgprint('str(attendance_role.max_permission_minutes)')
		# frappe.msgprint(str(attendance_role.max_permission_minutes))

		if perviuos_permission[0].total_min + duration > attendance_role.max_permission_minutes  :
			frappe.throw(_("Employee {} exceed the max Permission Minitues in  This Month \n Please Set Max Permission Minutes in Attendance Rule {}".format(self.employee,employee.attendance_rule)))

		if duration > attendance_role.max_permission_minute_per_once:
			frappe.throw(_("Employee {} Cann't exceed the max Permission Minitues in Per Time \n Please Set Max Permission Minitues per time in Attendance Rule {}".format(self.employee,employee.attendance_rule)))

		monthly_rate = frappe.db.sql("""
		select max_monthly_rate from `tabAttendence Permission Rule Table` where parent = '{parent}' and permission_type = '{type}' order by creation desc limit 1

		""".format(parent=attendance_role.name , type = self.permission_type),as_dict=1)

		perviuos_permission_type_mins = frappe.db.sql("""select 
						ifnull(SUM((TIME_TO_SEC(SUBTIME( ifnull(to_time,'00:00:00'), ifnull(from_time,'00:00:00'))) /60)),0) as total_min 
						from tabPermission where employee = '{employee}' 
						and date(date) between date('{start_date}')  and date('{end_date}') 
						and docstatus = 1 and status = 'Completed' and permission_type = '{type}' 
						and name <> '{name}'
						""".format(name=self.name,employee=self.employee, start_date=payroll_month.attendance_start_date,
								   end_date=payroll_month.attendance_end_date , type = self.permission_type), as_dict=1)
		if monthly_rate and perviuos_permission_type_mins :
			if float(monthly_rate[0].max_monthly_rate) < perviuos_permission_type_mins [0].total_min + duration :
				frappe.throw(_(
					"Employee {} exceed the max Permission Type Minitues in  This Month \n Please Set Max Permission Count in Attendance Rule {}".format(
						self.employee, employee.attendance_rule)))


	def updateStaus(self):
		EmpDepartment=frappe.db.sql("""
          select department from tabEmployee where name='{}'
			""".format(self.employee),as_dict=1)
		rolelist=frappe.db.sql("""
          select * from `tabDepartment Managment` where parent='{}'
			""".format(EmpDepartment[0]['department']),as_dict=1)
		docstatus=frappe.db.sql("""
              select status from tabPermission where name='{}'
			""".format(self.name),as_dict=1)
		rolee=""
		mylist=[]
		#index=0
		flag=0
		issubmitable=0
		#frappe.msgprint(rolelist[0].email)
		#frappe.throw(str(frappe.session.user))
		#frappe.msgprint(docstatus[0]["status"])
		for role in rolelist:
			
			#frappe.msgprint(frappe.session.user_email)
			#mylist.append(role.role_name)
			if role.email==str(frappe.session.user):
				rolee=role.role_name
				#index=len(mylist)
			if role.is_submitted ==1 and role.email==str(frappe.session.user):
				issubmitable=1
		if docstatus :
			if docstatus[0]["status"]=="Created" and rolee=="SuperVisor Approved":
				flag=1
			elif docstatus[0]["status"]=="SuperVisor Approved" and rolee=="Manager Approved":
				flag=1
			else:
				profile=frappe.db.sql("select role_profile_name from tabUser where name='{}'".format(str(frappe.session.user)),as_dict=1)
				#frappe.msgprint(profile[0]['role_profile_name'])
				if profile[0]['role_profile_name']=='hr' and docstatus[0]["status"]=="Manager Approved":
					flag=1
					rolee='Completed'
				else:
					flag=0


		if(flag==1):
			return rolee
		else:
			return 'false'


	def updateAction(self,Action):

		res1=frappe.db.sql("""update `tabPermission` set status='{}' where name='{}'""".format(Action,self.name))
		frappe.db.commit()
		if(Action=='Completed'):
			#frappe.msgprint(Action)
			frappe.db.sql("""update `tabPermission` set docstatus=1 where name='{}'""".format(self.name))
			frappe.db.commit()
			return "Done"
		if res1:
			return 'True'
		return res1

	def updateAction(self,Action):

		res1=frappe.db.sql("""update `tabMission` set status='{}' where name='{}'""".format(Action,self.name))
		frappe.db.commit()
		if(Action=='Completed'):
			#frappe.msgprint(Action)
			frappe.db.sql("""update `tabMission` set docstatus=1 where name='{}'""".format(self.name))
			frappe.db.commit()
			return "Done"
		if res1:
			return 'True'
		return res1
			
	def checkIfHasRoleSubmit(self):
		EmpDepartment=frappe.db.sql("""
          select department from tabEmployee where name='{}'
			""".format(self.employee),as_dict=1)
		rolelist=frappe.db.sql("""
          select * from `tabDepartment Managment` where parent='{}'
			""".format(EmpDepartment[0]['department']),as_dict=1)
		docstatus=frappe.db.sql("""
              select status from tabPermission where name='{}'
			""".format(self.name),as_dict=1)
		rolee=""
		mylist=[]
		for role in rolelist:
			if role.is_submitted ==1 and role.email==str(frappe.session.user):
				return 'true'
		return 'false'

	def Submitdoctype(self,Action):
		res1=frappe.db.sql("""update `tabPermission` set docstatus=1 where name='{}'""".format(self.name))
		frappe.db.commit()
		return "Done"

