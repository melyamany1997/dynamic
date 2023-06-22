# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import msgprint, _
class Mission(Document):

	def validate(self):
		# department=[]
		# rolelist=[]
		# department=frappe.db.sql("""select department from tabEmployee where name='{}'""".format(self.employee),as_dict=1)
		# asd=department[0].get('department')
		# #frappe.msgprint(asd)
		# if not asd:
		# 	frappe.throw("employee have no department")
		result=frappe.db.sql("""select * from tabMission 
			where name <> '{}' and
		  employee='{}'
		 and (start_time between '{}' and '{}' or 
		end_time between '{}' and '{}') and date='{}'
		""".format(self.name,self.employee,self.start_time,self.end_time,self.start_time,self.end_time,self.date),as_dict=1)
		
		if(len(result)>0):
			
			frappe.throw(_("Employee have mission in the same time"))

	def updateStaus(self):
		EmpDepartment=frappe.db.sql("""
          select department from tabEmployee where name='{}'
			""".format(self.employee),as_dict=1)

		rolelist=frappe.db.sql("""
          select * from `tabDepartment Managment` where parent='{}'
			""".format(EmpDepartment[0]['department']),as_dict=1)
		docstatus=frappe.db.sql("""
              select status from tabMission where name='{}'
			""".format(self.name),as_dict=1)
		rolee=""
		mylist=[]
		#index=0
		flag=0
		issubmitable=0
		if rolelist and docstatus:
			for role in rolelist:
				
				#frappe.msgprint(frappe.session.user_email)
				#mylist.append(role.role_name)
				if role.email==str(frappe.session.user):
					rolee=role.role_name
					#index=len(mylist)
				if role.is_submitted ==1 and role.email==str(frappe.session.user):
					issubmitable=1
			
			if docstatus[0].get("status")=="Created" and rolee=="SuperVisor Approved":
				flag=1
			elif docstatus[0].get("status")=="SuperVisor Approved" and rolee=="Manager Approved":
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
		return 'false'


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
              select status from tabMission where name='{}'
			""".format(self.name),as_dict=1)
		rolee=""
		mylist=[]
		for role in rolelist:
			if role.is_submitted ==1 and role.email==str(frappe.session.user):
				return 'true'
		return 'false'

	def Submitdoctype(self,Action):
		res1=frappe.db.sql("""update `tabMission` set docstatus=1 where name='{}'""".format(self.name))
		frappe.db.commit()
		return "Done"



		
		   
		
				


			







	
