# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils.background_jobs import enqueue
from frappe.model.document import Document
from datetime import datetime,timedelta,time,date
from dateutil.relativedelta import relativedelta
from frappe.utils import now, cint, get_datetime, to_timedelta,update_progress_bar,background_jobs
from erpnext.hr.doctype.employee.employee import get_holiday_list_for_employee



# Type Number Codes : 
# 	1 => Present
# 	2 => Absent
# 	3 => Leave
# 	4 => Holiday
# 	5 => Business Trip
#   6 => Mission
#   7 => Mission All Day
#   8 => Half Day
#   9 => Working On Holiday
#   10 => Week End
#   11 => Sick Leave
#   12 => Privilege Leave
#   13 => Working On Weekend
#   14 => Hold
#   15 => 
#   16 => 
#   17 => 
#   18 => 

class AttendanceCalculation(Document):
	# attendances = []
	# employees = []
	def on_cancel (self):
		self.update_attendance_logs(status=0)
		self.delete_Additional_salary()

	def on_submit(self,grade=None, department=None, designation=None,employee=None):
		conditions = ""
		if employee:
			conditions += " and e.name = '{}'".format(str(employee))
		else:
			if grade:
				conditions += " and e.grade = '{}'".format(str(grade))
			if designation:
				conditions += " and e.designation = '{}'".format(str(designation))
			if department:
				conditions += " and e.department = '{}'".format(str(department))

		self.post_attendance(conditions)
		self.update_attendance_logs(status = 1)

	def update_attendance_logs (self , status = 1):
		frappe.db.sql (""" 
		update `tabAttendance` set docstatus = {status} , is_calculated = {status} where   date(attendance_date) between date('{from_date}') and date ('{to_date}') ;
		""".format(status=status  , from_date = self.from_date , to_date = self.to_date ))
	def Calculate_attendance(self,grade=None, department=None, designation=None,employee=None):
		self.validate()

		conditions = ""
		if employee :
			conditions += " and emp.name = '{}'".format(str(employee))
		else :
			if grade :
				conditions += " and emp.grade = '{}'".format(str(grade))
			if designation :
				conditions += " and emp.designation = '{}'".format(str(designation))
			if department :
				conditions += " and emp.department = '{}' ".format(str(department))
		attendacne_sql= """
			select emp.name as employee , Date(log_time) as Day  , MIN(log_time) as 'IN' ,
			 MAX(log_time) as 'OUT'
			from  `tabEmployee` emp
			LEFT join `tabDevice Log` on emp.attendance_device_id = `tabDevice Log`.enroll_no
			where emp.name is not null and emp.company = '{company}'
			{conditions}
			group by Date(log_time),emp.name
			having  Day between '{from_date}' and '{to_date}'
			
			""".format(company=self.company, from_date=self.from_date,to_date=self.to_date,conditions=conditions)
		self.attendances = frappe.db.sql(attendacne_sql,as_dict=1)
		day = datetime.strptime(str(self.from_date),'%Y-%m-%d').date()
		self.to_date = datetime.strptime(str(self.to_date),'%Y-%m-%d').date()
		# today = date.today()
		# if today < self.to_date :
		# 	self.to_date = today
		self.from_date = datetime.strptime(str(self.from_date),'%Y-%m-%d').date()
		self.employees = frappe.db.sql (""" select name from tabEmployee emp where 1=1  {conditions}""".format(conditions=conditions),as_list=1)

		result = []
		if  self.employees:
			# for  employee in self.employees:
			# self.enqueue_calculate()
				if len(self.employees) > 50 :
					enqueue(enqueue_calculate ,queue='background', timeout=3000, now=True,   self= self , employees = self.employees)
				else :
					enqueue_calculate(self,self.employees)
					# self.enqueue_calculate()
		frappe.msgprint(_("Done") , indicator='green')



		# return True

	def calculate(self,employee , day , flag = None , missions=[] , businessTrips=[] , permissions=[] ):
		self.emp = frappe.get_doc("Employee", employee)
		joining_date, relieving_date = frappe.get_cached_value("Employee", employee,["date_of_joining", "relieving_date"])
		if joining_date and day < joining_date:
			return
		if relieving_date and day > relieving_date:
			return
		self.date_time = datetime.strptime(str(day) , '%Y-%m-%d')

		frappe.db.sql("delete from tabAttendance where employee = '{}' and attendance_date = date('{}') ; ".format(employee ,day ))
		frappe.db.commit()
		doc = frappe._dict()
		if flag :
				doc.weekend = 1

		# doc.name = "Att-{employee}-{date}".format(employee=str(employee) , date = str(day))
		doc.employee = employee
		doc.date = day
		doc.early_in = timedelta (minutes=0)
		doc.early_out = timedelta (minutes=0)
		doc.late_in = timedelta (minutes=0)
		doc.late_out = timedelta (minutes=0)
		doc.total_wrking_hours= timedelta (minutes=0)
		doc.overtime_mins = timedelta (minutes=0)
		doc.overtime_factor = 0
		doc.late_minutes = timedelta (minutes=0)
		doc.late_factor = 0
		doc.less_time =  timedelta (minutes=0)
		doc.less_time_penalty =  0
		doc.less_time_factor =  0
		doc.leave_factor = 0
		doc.calculate_overtime = 0
		doc.is_open_shift = 0
		doc.is_24_hours = 0
		doc.permission_minutes = 0


		Holidays = None
		Leaves = None
		Shift = None
		self.Permissions = [x for x in permissions if x.date == day]
		doc.is_calculated=0


		default_shift = get_employee_shift(employee, day, True)

		if default_shift and default_shift.shift_type:
			doc.shift_working_hours = default_shift.working_hours
			doc.start_time = default_shift.start_time
			doc.end_time = default_shift.end_time
			doc.is_flexible_hours = default_shift.is_flexible_hours
			doc.custom_start_end = default_shift.custom_start_end
			doc.is_open_shift = default_shift.shift_type.is_open_shift
			doc.is_24_hours = default_shift.shift_type.is_24_hours

		holiday_list  = get_holiday_list_for_employee(employee, False)


		if default_shift and not holiday_list:
				holiday_list = default_shift.holiday_list #frappe.db.get_value('Shift Type', default_shift, ['holiday_list'])

		if not holiday_list:
			frappe.msgprint(_("Please Set Default Holiday List In Company or in {} Employee" .format(employee)),indicator='red')
			return
		if not default_shift:
			frappe.msgprint(_("Please Assign Shift or Set Default Shift Type  In Employee {} or in Company").format(employee),indicator='red')
			return
		doc.company = self.company

		Holidays = frappe.db.sql("""
			select * from `tabHoliday` where parent = '{holiday_list}' and holiday_date = '{day}'
			""".format(holiday_list=holiday_list,day=day),as_dict=1)
		Shift = default_shift #frappe.db.get_value('Shift Type', default_shift, ['start_time', 'end_time'], as_dict=1)
		doc.Shift = Shift
		doc.shift_start = self.date_time
		doc.shift_end = self.date_time

		if Shift.start_time :
			doc.shift_start +=Shift.start_time
		if Shift.end_time :
			doc.shift_end +=Shift.end_time

		if doc.is_open_shift :
			doc.shift_end += timedelta(days=1)

		doc.shift_actual_start = ''
		doc.shift_actual_end = ''
		doc.shift = default_shift.name
		# doc.is_open_shift = Shift.is_open_shift
		user_records_in_day = []
		# frappe.msgprint(str(Shift))

		if not doc.is_open_shift :
			# user_records_in_day = frappe.db.sql("""
			# 						select emp.name as employee , Date(log_time) as Day  , MIN(log_time) as 'IN' ,  MAX(log_time) as 'OUT'  from `tabDevice Log`
			# 						inner join `tabEmployee` emp on emp.attendance_device_id = `tabDevice Log`.enroll_no
			# 						where emp.name is not null and emp.company = '{company}'
			# 						group by Date(log_time),emp.name
			# 						having  Day = date('{day}')
			# 						""".format(company=self.company, day = day), as_dict=1)
			user_records_in_day = [x for x in self.attendances if x.employee == employee and x.Day == day]
		else :
			if doc.is_open_shift and not doc.is_24_hours :
				#Open Shift
				from_time = doc.shift_start - timedelta (hours=4)
				to_time = doc.shift_end + timedelta (hours=4)
				sql = """
				select 
								MIN(log_time) as 'IN' ,  
								MAX(log_time) as 'OUT'   
						from `tabDevice Log`
						inner join `tabEmployee` emp on emp.attendance_device_id = `tabDevice Log`.enroll_no
						where emp.name = '{employee}' and log_time between '{from_time}' and '{to_time}'
						group by emp.name  
						
				""".format(employee=employee, from_time =from_time, to_time =to_time)
				user_records_in_day = []
				user_records_in_day=  frappe.db.sql( sql, as_dict=1)
			elif doc.is_open_shift and  doc.is_24_hours :
				# Shift 24 Hours
				from_time_in = doc.shift_start - timedelta(hours=4)
				to_time_in = doc.shift_start + timedelta(hours=4)
				from_time_out = to_time_in
				to_time_out = doc.shift_end + timedelta(hours=4)
				last_day = doc.date - timedelta ( days =1)
				sql = """
								select 
										MIN(case when log_time between '{from_time_in}' and '{to_time_in}' then log_time end ) as 'IN' ,  
										MAX(case when log_time between '{from_time_out}' and '{to_time_out}' then log_time end ) as 'OUT'   
										from `tabDevice Log`
										inner join `tabEmployee` emp on emp.attendance_device_id = `tabDevice Log`.enroll_no
										where emp.name = '{employee}' 
										and log_time between '{from_time_in}' and '{to_time_out}'  
										and ( select count(name) from tabAttendance where employee = '{employee}' 
                                          and attendance_date = date('{last_day}') 
                                          and status != 'Present' ) >= 1
										group by emp.name   ;

								""".format(employee=employee, from_time_in=from_time_in, to_time_in=to_time_in
										   , from_time_out = from_time_out , to_time_out = to_time_out
										   ,last_day = last_day , today = doc.date  )
				# frappe.msgprint(sql)
				user_records_in_day = None
				user_records_in_day = frappe.db.sql(sql, as_dict=1)
				if user_records_in_day :
					if not user_records_in_day[0].OUT :
						user_records_in_day[0].OUT = user_records_in_day[0].IN
					if not user_records_in_day[0].OUT or not user_records_in_day[0].IN :
						user_records_in_day = None

		# BusinessTrips = frappe.db.sql("""
		# select * from `tabBusiness Trip` where docstatus = 1 and from_date <= '{day}' and to_date >= {day}
		# 											and employee = '{employee}'
		# 											""".format(day=day, employee=employee), as_dict=1)


		# self.Permissions = frappe.db.sql("""
		# 	select permission.name , type.code , SUBTIME (permission.to_time,permission.from_time) as Duration
		# 	from tabPermission permission inner join `tabPermission Type` type on type.name = permission.permission_type where permission.docstatus = 1 and status = "Completed" and date(date) = date('{day}') and employee = '{employee}'
		# 	group by  permission.name ;
		# """.format(day = day , employee = employee),as_dict=1)
		# missions = frappe.db.sql("""
		# 							select * from `tabMission` where docstatus = 1 and tabMission.date = '{day}'  and employee = '{employee}' order by start_time asc ,  end_time asc
		# 							""".format(day=day, employee=employee), as_dict=1)
		self.missions = [x for x in missions  if x.date == day]
		self.BusinessTrips= [x for x in businessTrips if x.from_date <= day <= x.to_date  ]

		if self.emp.status == 'Hold' and doc.date <= self.emp.hold_date:
			doc = self.Hold(doc)

		else:
			if Holidays :
				# Day is Holiday
				if not user_records_in_day:
					if (len(self.missions or []) > 0) or (len(self.BusinessTrips or []) > 0)  :
						if Holidays[0].weekly_off :
							doc = self.Present(doc,user_records_in_day,Shift ,type =6)
						else:
							doc = self.Present(doc,user_records_in_day,Shift ,type =5)

					else:
						doc.reference_type = "Holiday List"
						doc.reference_name =  	holiday_list
						if Holidays[0].weekly_off :
							doc = self.In_Holiday(doc , type = 'Weekend')
						else:
							doc = self.In_Holiday(doc , type = 'Official')

				else :
					if Holidays[0].weekly_off :
						doc = self.Present(doc,user_records_in_day[0],Shift ,type =6)
					else:
						doc = self.Present(doc,user_records_in_day[0],Shift ,type =5)

			else :
				# Not Holiday
				Leaves = frappe.db.sql("""
				select * from `tabLeave Application` where employee = '{employee}' and from_date <= '{day}' and to_date >= '{day}' and docstatus = 1 and status = 'Approved'
				""".format(employee=employee,day=day),as_dict=1)
				if Leaves :
					# In Leave
					doc.reference_type = "Leave Application"
					doc.reference_name =  	Leaves[0].name
					doc.leave_type =  	Leaves[0].leave_type

					if  Leaves[0].half_day:
						if Leaves[0].half_day_date == day :
							if user_records_in_day :
								# Present in Half Day
								doc = self.Present(doc,user_records_in_day[0],Shift ,type =4)
							else :
								# half day with no records
								if len(self.missions or []) > 0 or  len(self.BusinessTrips or []) > 0:
									doc = self.Present(doc, user_records_in_day, Shift, type=4)

								else:
									doc = self.Absent(doc)
					else:

						doc.leave_type = Leaves[0].leave_type
						doc.leave_application = Leaves[0].name
						doc = self.In_Leave (doc)
				else :

					if len(self.BusinessTrips or []) > 0:
						doc.reference_type = "Business Trip"
						doc.reference_name =  	self.BusinessTrips[0].name
						doc = self.Present(doc, user_records_in_day, Shift)


					else :

							# doc.reference_type = "Shift Type"
							# doc.reference_name = default_shift
							# frappe.msgprint(str(datetime.strptime(x.Day,"%Y-%m-%d") for x in self.attendances) + "  " + str(day))

							if len(self.missions or []) > 0  and user_records_in_day:
								doc = self.Present(doc,user_records_in_day[0],Shift ,missions=self.missions,type =2)

							elif len(self.missions or []) > 0 and not user_records_in_day:
								doc = self.Present(doc,user_records_in_day,Shift ,missions = self.missions,type =3)
							elif not user_records_in_day:
								# Absent
								if doc.weekend == 1:
									doc = self.In_Holiday(doc, type='Weekend')
								else :
									doc = self.Absent(doc)
							elif user_records_in_day:
								# Present
								doc = self.Present(doc,user_records_in_day[0],Shift)
		attendance = frappe.new_doc("Attendance")
		if getattr(doc, 'attendance_request', None):
			attendance.attendance_request = doc.attendance_request
		attendance.flags.ignore_validate = True
		attendance.employee = doc.employee or ''
		attendance.attendance_date = doc.date
		attendance.overtime_in = doc.early_in or timedelta(minutes=0)
		attendance.old_overtime_in = doc.early_in or timedelta(minutes=0)
		attendance.early_in = doc.early_in or timedelta(minutes=0)
		attendance.early_out = doc.early_out or timedelta(minutes=0)
		attendance.late_in = doc.late_in if doc.late_factor else  timedelta(minutes=0)
		attendance.late_penality = doc.late_penality or 0
		attendance.overtime_out = doc.late_out if doc.overtime_factor  else  timedelta(minutes=0)
		attendance.old_overtime_out = doc.late_out or timedelta(minutes=0)
		attendance.shift_working_hours = doc.shift_working_hours

		attendance.working_hours = float((doc.total_wrking_hours.seconds / 3600)+ (doc.total_wrking_hours.days * 24))   or 0
		attendance.overtime_mins = doc.overtime_mins or timedelta (minutes=0)
		attendance.old_overtime_mins = doc.overtime_mins or timedelta (minutes=0)
		attendance.old_overtime_factor = doc.overtime_factor or 0
		attendance.fingerprint_factor = getattr(doc,'fingerprint_factor',0)
		attendance.overtime_factor = doc.overtime_factor or 0
		attendance.calculate_overtime = doc.calculate_overtime or None
		attendance.less_time_penalty = doc.less_time_penalty or 0
		attendance.less_time_factor = doc.less_time_factor or 0
		attendance.late_minutes = doc.late_minutes or timedelta (minutes=0)
		attendance.late_factor = doc.late_factor or 0
		attendance.less_time = doc.less_time or timedelta(minutes=0)
		attendance.permission_minutes = doc.permission_minutes or 0
		attendance.company = doc.company or ''
		attendance.shift = doc.shift or ''
		attendance.status = doc.type or ''
		attendance.type_number = doc.type_number
		attendance.attendance_calculation = self.name
		attendance.fingerprint_type = doc.fingerprint_type or ''
		attendance.forget_fingerprint = doc.forget_fingerprint or 0
		attendance.work_from_home = getattr(doc,'work_from_home',0)
		attendance.early_exit = doc.early_exit or 0
		attendance.late_entry = doc.late_entry or 0
		attendance.late_componant =doc.late_componant or None
		attendance.leave_factor = doc.leave_factor

		if doc.fingerprint_type == 'OUT' :
			# Forgetten is OUT
			doc.shift_actual_end = ''
			doc.late_out = timedelta(minutes=0)
			doc.early_out = timedelta(minutes=0)
		elif doc.fingerprint_type == 'IN':
			# Forgetten is IN
			doc.shift_actual_end = ''
			doc.early_in = timedelta(minutes=0)
			doc.late_in = timedelta(minutes=0)

		if doc.shift_actual_start != '' :
			attendance.attend_time = doc.shift_actual_start.time() or ''
			# doc.shift_actual_start = doc.shift_actual_start.time()
			attendance.in_time =  doc.shift_actual_start

		else:
			attendance.attend_time = ''
			attendance.in_time = ''

		if doc.shift_actual_end != '' :
			attendance.leave_time = doc.shift_actual_end.time()
			attendance.out_time = doc.shift_actual_end
			# attendance.out_time = datetime.combine(doc.date, doc.shift_actual_end)
		else:
			attendance.leave_time = ''
			attendance.out_time = ''
		if doc.shift_start != '' :
			# doc.shift_start = doc.shift_start.time()
			attendance.shift_start =  doc.shift_start
		else:
			attendance.shift_start = ''
		if doc.shift_end != '' :
			# doc.shift_end = doc.shift_end.time()
			attendance.shift_end = doc.shift_end
		else:
			attendance.shift_end = ''

		# attendance.shift_start =datetime.strptime(str(str(doc.date)+ ' '+ str(doc.shift_start)), '%Y-%m-%d %H:%M:%S') or ''
		# attendance.shift_start =datetime.combine(doc.date, doc.shift_start) or ''
		# attendance.shift_end =datetime.combine(doc.date, doc.shift_end) or ''
		# attendance.out_time =datetime.combine(doc.date, doc.shift_actual_end)
		attendance.holiday = doc.holiday or 0
		attendance.weekend = doc.weekend or 0
		attendance.permission = doc.permission or 0
		attendance.mission = doc.mission or 0
		attendance.bussines_trip = doc.bussines_trip or 0
		attendance.party_type = doc.reference_type
		attendance.part_name = doc.reference_name
		attendance.naming_series = "HR-ATT-.YYYY.-"
		attendance.leave_application =doc.leave_application or ''
		attendance.leave_type = doc.leave_type or ''
		attendance.insert()
		attendance.submit()


		#doc.insert()

	def In_Holiday (self,doc,type = 'Weekend'):
		if type == 'Weekend' :
			doc.weekend = 1
			doc.type = "Weekend"
			doc.type_number = 10
		else :
			doc.holiday = 1
			doc.type = "Holiday"
			doc.type_number = 4
		# doc.insert()
		return doc

	def In_BusinessTrip (self,doc):
		doc.bussines_trip = 1
		doc.type = "Business Trip"
		doc.type_number = 5
		# doc.insert()
		return doc

	def In_Leave (self,doc):
		doc.type = "On Leave"

		doc.type_number = 3
		return self.calculate_leave_factor(doc,half_day=0)

	def Hold (self,doc):
		doc.type = "Hold"
		doc.type_number = 14
		return doc

	def Absent (self,doc):
		doc = self.check_attendance_request(doc)
		if getattr(doc,'attendance_request',None):
			log = frappe._dict()
			log.IN = doc.request.from_time
			log.OUT = doc.request.to_time
			doc = self.Present(doc,log,doc.Shift ,type =8)
		else:
			doc.type = "Absent"
			doc.type_number = 2
		return doc
	def check_attendance_request (self,doc):
			list = frappe.db.sql("""
			select * from `tabAttendance Request` where docstatus = 1
			 and employee = '{}' and date('{}') between from_date and to_date 
			 order by modified desc limit 1
			""".format(doc.employee,doc.date),as_dict=1)
			if list:
				request = list[0]
				doc.attendance_request = request.name
				doc.request = request
			return doc


	def Present (self,doc , log ,shift , missions = None ,  type = 1):
		# type document 
		#	1 => Normal Present 
		#	2 => Present With Missions in day
		#	3 => Present With missions all the day
		#	4 => Half Day
		#	5 => Working On Holiday
		#
		#
		#
		#
		# doc.reference_type= "Shift Type"
		# doc.reference_name= shift.name
		doc = self.check_attendance_request(doc)
		doc.type = "Present"
		doc.type_number = 1

		IN = None
		OUT = None
		doc.overtime_request = 0
		if type == 8:
			IN = self.date_time + to_timedelta(str(log.IN))
			OUT = self.date_time + to_timedelta(str(log.OUT))
			if shift.is_open_shift:
				OUT += timedelta(days=1)
			# IN = to_timedelta(str(log.IN))
			# OUT = to_timedelta(str(log.OUT))
			doc.work_from_home = 1
			if doc.request.reason == 'Overtime':
				doc.overtime_request = 1
		else :
			doc = self.check_attendance_request(doc)

			if getattr(doc,'attendance_request',None):
				if doc.request.reason == 'Overtime':
					doc.overtime_request = 1



		if len(self.BusinessTrips or []) > 0:
			log = frappe._dict()
			log.IN = self.date_time + shift.start_time
			log.OUT = self.date_time + shift.end_time
			doc.bussines_trip = 1
			# doc.insert()
		if len(self.missions or []) > 0  and log :
			# Present With Missions in day
			doc.mission = 1
			# doc.type = "Mission"
			doc.type_number = 6
			if self.missions[0].start_time < to_timedelta(str(log.IN.time())):
				IN = self.missions[0].start_time
			else :
				IN = to_timedelta(str(log.IN.time()))
			if self.missions[-1].end_time > to_timedelta(str(log.OUT.time())):
				OUT = self.missions[-1].end_time
			else:
				OUT = to_timedelta(str(log.OUT.time()))

			IN += self.date_time
			OUT +=  self.date_time
		elif self.missions and not log :
			# Present With missions all the day
			doc.mission = 1
			# doc.type = "Prese"
			doc.type_number = 7
			IN = self.missions[0].start_time + self.date_time
			OUT = self.missions[-1].end_time + self.date_time
			log = frappe._dict()
			log.IN = self.date_time + shift.start_time
			log.OUT = self.date_time + shift.end_time



		if type == 4 :
			# Half Day
			# doc.type = "Half Day"
			doc.type_number = 8
			# IN = to_timedelta(str(log.IN.time()))
			# OUT = to_timedelta(str(log.OUT.time()))
			IN = log.IN
			OUT = log.OUT
			doc = self.calculate_leave_factor(doc,half_day=1)

		if type == 1 :
			# Normal Present
			# IN = to_timedelta(str(log.IN.time()))
			# OUT = to_timedelta(str(log.OUT.time()))
			IN = log.IN
			OUT = log.OUT
		if type == 5:
			# Working On Holiday
			doc.holiday = 1
			# doc.type = "Working On Holiday"
			doc.type_number = 9
			# IN = to_timedelta(str(log.IN.time()))
			# OUT = to_timedelta(str(log.OUT.time()))
			IN = log.IN
			OUT = log.OUT
		if type == 6:
			# Working On Holiday
			doc.weekend = 1
			# doc.type = "Working On Weekend"
			doc.type_number = 13
			# IN = to_timedelta(str(log.IN.time()))
			# OUT = to_timedelta(str(log.OUT.time()))
			IN = log.IN
			OUT = log.OUT


		# frappe.msgprint(str(IN))
		doc.shift_actual_start = IN
		doc.shift_actual_end = OUT





		shift.start_time = self.date_time + shift.start_time
		shift.end_time = self.date_time + shift.end_time
		if shift.is_open_shift or shift.start_time.time() > shift.end_time.time()  :
			shift.end_time +=  timedelta (days=1)


		doc.early_in = shift.start_time - IN
		doc.late_in =  IN - shift.start_time

		doc.early_out =  shift.end_time  - OUT
		doc.late_out = OUT - shift.end_time




		if doc.early_in < timedelta(minutes=0):
			doc.early_in = timedelta(minutes=0)
		if doc.early_out < timedelta(minutes=0):
			doc.early_out = timedelta(minutes=0)
		if doc.late_out < timedelta(minutes=0):
			doc.late_out = timedelta(minutes=0)
		if doc.late_in < timedelta(minutes=0):
			doc.late_in = timedelta(minutes=0)
		if IN == OUT:
			doc = self.forget_fingerPrint(doc)

		working_in = doc.shift_actual_start or shift.start_time
		working_out = doc.shift_actual_end or shift.end_time
		doc.total_wrking_hours = working_out - working_in


		# flixeble Hours

		if doc.is_flexible_hours:
			doc.late_in =  timedelta(minutes=0)
			doc.early_in = timedelta(minutes=0)
			doc.early_out = timedelta(minutes=0)
			doc.late_out = timedelta(minutes=0)
			if doc.custom_start_end:
				start_time = doc.start_time or doc.shift_start
				end_time = start_time + doc.total_wrking_hours
				if start_time < to_timedelta(str(doc.shift_actual_start.time())):
					doc.late_in =   to_timedelta(str(doc.shift_actual_start.time())) - start_time

			# working Hours

			diff = abs(doc.shift_working_hours - ((doc.total_wrking_hours.seconds /3600) + doc.total_wrking_hours.days *24))
			sec = diff * 3600
			if doc.shift_working_hours  > ((doc.total_wrking_hours.seconds /3600) + doc.total_wrking_hours.days *24) :

				doc.early_out  = timedelta(seconds=sec) - doc.late_in

			else :
				doc.late_out = timedelta(seconds=sec)


		# In Time
		# Out Time
		if len(self.Permissions  or []) > 0:
			doc.permission = 1
			for i in self.Permissions:
				if i.code == 1:
					# start of the Day
					doc.late_in -= i.Duration
					doc.early_in = timedelta(minutes=0)
				elif i.code == 2:
					# end of the day
					doc.late_out = timedelta(minutes=0)
					doc.early_out -= i.Duration
				doc.reference_type = "Permission"
				doc.reference_name = i.name
		if doc.late_in > timedelta(minutes=0):
			doc.late_entry = 1
		if doc.early_out > timedelta(minutes=0):
			doc.early_exit = 1
		if doc.early_in < timedelta(minutes=0):
			doc.early_in = timedelta(minutes=0)
		if doc.early_out < timedelta(minutes=0):
			doc.early_out = timedelta(minutes=0)
		if doc.late_out < timedelta(minutes=0):
			doc.late_out = timedelta(minutes=0)
		if doc.late_in < timedelta(minutes=0):
			doc.late_in = timedelta(minutes=0)
		employee = self.emp
		doc.less_time = doc.early_out
		if employee.has_attendance_rule and employee.attendance_rule:
			attendance_role = frappe.get_doc("Attendance Rule", employee.attendance_rule)

			if doc.type in ["Present"]:
				if attendance_role.calculate_early_in:
					doc.overtime_mins = doc.early_in + doc.late_out
				else :
					doc.overtime_mins = doc.late_out

				if attendance_role.deduct_overtime_from_delays:

					if doc.late_in.seconds > doc.overtime.seconds :
						doc.late_in -= doc.overtime_mins
						doc.overtime_mins = timedelta(minutes=0)

					else:
						doc.overtime_mins -= doc.late_in
						doc.late_in = timedelta(minutes=0)



				# Calculate delayes

				# first Deduct Lates from permission balance
				if attendance_role.deduct_lates_permission :
					balance = (attendance_role.max_permission_minutes or 0) - (self.permission_taken_minutes + self.used_permission_balance)
					taken = 0
					if balance > 0 :
						balance_in_time = timedelta(minutes=balance)
						if doc.late_in > balance_in_time :
							doc.late_in -= balance_in_time
							taken = balance
						else :
							taken=int(doc.late_in.seconds /60)
							doc.late_in = timedelta(minutes=0)
					doc.permission_minutes += taken
					self.permission_taken_minutes += taken
				if doc.late_in > timedelta(minutes=0):
					doc = self.calculate_Delays(doc,employee,attendance_role)

				# Calculate Overtime
				if ((employee.enable_overtime and attendance_role.enable_overtime) or doc.overtime_request ) and doc.overtime_mins > timedelta(minutes=0):
					if not attendance_role.need_to_approve or doc.overtime_request:
						doc.calculate_overtime = 1
					doc = self.calculate_overtime(doc,employee,attendance_role)
				# Calculate Lesstime

				# first Deduct Lates from permission balance
				if attendance_role.deduct_less_permission:
					balance = (attendance_role.max_permission_minutes or 0) - (
								self.permission_taken_minutes + self.used_permission_balance)
					taken = 0
					if balance > 0:
						balance_in_time = timedelta(minutes=balance)
						if doc.early_out > balance_in_time:
							doc.early_out -= balance_in_time
							taken = balance
						else:
							taken = int(doc.early_out.seconds / 60)
							doc.early_out = timedelta(minutes=0)


					doc.permission_minutes += taken
					self.permission_taken_minutes += taken

				if doc.early_out > timedelta(minutes=0):
						doc = self.calculate_less_time(doc ,attendance_role)
				if doc.forget_fingerprint :
						self.calculate_Finger_print(doc,employee,attendance_role)


			else:
				doc.overtime_mins = ''
				doc.overtime_factor = 0

		# doc.overtime_factor = timedelta(minutes=doc.overtime_factor)

		return doc


	def forget_fingerPrint (self,doc):
		doc.forget_fingerprint = 1
		in_min = abs((doc.early_in + doc.late_in).seconds / 60)
		out_min = abs((doc.early_out +  doc.late_out).seconds / 60)
		if not doc.is_24_hours :
			if in_min <= out_min :
				# Forgetten is OUT
				doc.fingerprint_type='OUT'
				doc.shift_actual_end = doc.shift_end
				doc.late_out = timedelta(minutes=0)
				doc.early_out = timedelta(minutes=0)
			else:
				# Forgetten is IN
				doc.fingerprint_type = 'IN'
				doc.shift_actual_start = doc.shift_start
				doc.early_in = timedelta(minutes=0)
				doc.late_in = timedelta(minutes=0)
		else :
			# Forgetten is OUT
			doc.fingerprint_type = 'OUT'
			doc.shift_actual_end = doc.shift_end
			doc.late_out = timedelta(minutes=0)
			doc.early_out = timedelta(minutes=0)

		return doc


	def calculate_Delays(self,doc,employee , attendance_role):
		# employee = frappe.get_doc("Employee",doc.employee)
		doc.late_penality = 0
		doc.late_factor = 0
		doc.less_time =  timedelta(minutes=0)
		if attendance_role.enable_late_penality :
			if attendance_role.type == "Daily" and attendance_role.working_type == "Shift":
				if doc.type == "Present" and doc.holiday:
					if not attendance_role.caclulate_deduction_in_working_on_holiday :
						return doc
				if doc.type == "Present" and doc.holiday:
					if not attendance_role.caclulate_deduction_in_working_on_weekend :
						return doc
				if not attendance_role.late_role_table :
					frappe.msgprint(_("this Rule {} doesn't Contain Attendance Late Rules".format(attendance_role.name)))

				if  attendance_role.late_role_table :
					if attendance_role.type == 'Daily':
						late_minutes = doc.late_in.seconds /60
						doc.late_minutes = timedelta(minutes=late_minutes)
						penality = None
						for i in attendance_role.late_role_table:

							if i.from_min <= late_minutes  :
								penality = i


						if penality :
							doc.late_componant = penality.late_componant


							perviuos_penality_component = frappe.db.sql("""
							select count(*) as count from `tabAttendance` where employee = '{employee}' and date(attendance_date) between date('{from_date}') and date('{to_date}') and late_componant = '{component}'
							""".format(employee=employee.name , from_date = self.payroll_start_date , to_date = doc.date , component = penality.late_componant ))
							level = perviuos_penality_component [0][0] + 1
							message = "employee {} ".format(employee.name) + "date {}".format(doc.date) + " Level {}".format(level) + "component {}".format( penality.late_componant)

							level_factor = 0
							if level == 1  :
								level_factor = penality.level_onefactor
							elif level == 2  :

								level_factor = penality.level_towfactor
							elif level == 3 :

								level_factor = penality.level__threefactor
							elif level == 4 :

								level_factor = penality.level_fourfactor
							elif level == 5  :

								level_factor = penality.leve_five_factor
							else:

								level_factor = penality.leve_five_factor or penality.level_fourfactor or penality.level__threefactor or penality.level_towfactor or penality.level_onefactor or 0

							doc.late_penality = level_factor * penality.factor

							if penality.add_deduction:
								if penality.deduction_factor :
									doc.late_factor = penality.deduction_factor
								else:
									doc.late_factor = doc.late_in.seconds/60

			elif attendance_role.type == "Daily" and attendance_role.working_type == "Target Hours":
				if attendance_role.total_working_hours_per_day:
					total = timedelta (hours=attendance_role.total_working_hours_per_day)
					if total > doc.total_wrking_hours :
						doc.less_time = total - doc.total_wrking_hours
		if doc.late_factor:
			doc.late_factor = timedelta (minutes=doc.late_factor)
		return doc
	def calculate_Finger_print(self,doc,employee , attendance_role):
		# employee = frappe.get_doc("Employee",doc.employee)
		doc.fingerprint_factor = 0
		if attendance_role.enable_fingerprint_penality and getattr(doc,'forget_fingerprint',0):

			if doc.type == "Present" and doc.holiday:
				if not attendance_role.caclulate_deduction_in_working_on_holiday :
					return doc
			if doc.type == "Present" and doc.holiday:
				if not attendance_role.caclulate_deduction_in_working_on_weekend :
					return doc
			if not attendance_role.late_role_table :
				frappe.msgprint(_("this Rule {} doesn't Contain Attendance Late Rules".format(attendance_role.name)))

			if  getattr(attendance_role,'fingerprint_factors',None) :
				perviuos = frappe.db.sql("""
				select count(forget_fingerprint)+1 as count from `tabAttendance`
					where employee = '{employee}'
					  and date(attendance_date) between date('{from_date}') and date('{to_date}')
					  and forget_fingerprint = 1
				""".format(employee=doc.employee, from_date=self.payroll_start_date, to_date=doc.date))[0][0] or 1

				if perviuos > len(attendance_role.fingerprint_factors):
					doc.fingerprint_factor = attendance_role.fingerprint_factors [-1].factor
				else :

					doc.fingerprint_factor = attendance_role.fingerprint_factors[int(perviuos)-1].factor



			else :
					doc.fingerprint_factor = getattr(attendance_role,'fingerprint_forgetten_out_penality',0)
		return doc

	def calculate_overtime(self,doc,employee,attendance_role):
		overtime_factor = 0
		overtime_mins = 0
		if (employee.enable_overtime and attendance_role.enable_overtime) or doc.overtime_request :

			if attendance_role.type == "Daily" and attendance_role. working_type == "Shift":
					if doc.type == "Present" and doc.holiday:

						if attendance_role.max_overtime_hours_in_holiday:
							if doc.total_wrking_hours.seconds  /3600 > attendance_role.max_overtime_hours_in_holiday:
								overtime_mins = attendance_role.max_overtime_hours_in_holiday * 60
							elif attendance_role.calculate_all_day_in_holiday :
								if (doc.total_wrking_hours.seconds  /3600) < attendance_role.total_working_hours_per_day:
									overtime_mins = attendance_role.total_working_hours_per_day * 60
						if not overtime_mins :
							overtime_mins = doc.total_wrking_hours.seconds /60
						if attendance_role.overtime_factor_in_holidays:
							overtime_factor = overtime_mins *  attendance_role.overtime_factor_in_holidays
						doc.overtime_mins  =  doc.total_wrking_hours

					elif doc.type == "Present" and doc.weekend:

						if attendance_role.overtime_factor_in_weekend:
							if doc.total_wrking_hours.seconds  /3600 > attendance_role.max_overtime_hours_in_weekend:
								overtime_mins = attendance_role.max_overtime_hours_in_weekend * 60
							elif attendance_role.calculate_all_day_in_weekend :
								if (doc.total_wrking_hours.seconds  /3600) < attendance_role.total_working_hours_per_day:
									overtime_mins = attendance_role.total_working_hours_per_day * 60
						if not overtime_mins :
							overtime_mins = doc.total_wrking_hours.seconds /60
						if attendance_role.overtime_factor_in_weekend:
							overtime_factor = overtime_mins *  attendance_role.overtime_factor_in_weekend
						doc.overtime_mins  = doc.total_wrking_hours

					elif doc.type == "Present" :

						if attendance_role.max_overtime_hours_per_day:
							if doc.overtime_mins > timedelta(hours=attendance_role.max_overtime_hours_per_day):
								doc.overtime_mins = timedelta(hours=attendance_role.max_overtime_hours_per_day)
						overtime_mins = doc.overtime_mins.seconds /60
						if attendance_role.overtime_rules:
							# calcuate based on rules
							for i in attendance_role.overtime_rules :
								if  i.from_min <= overtime_mins <= i.to_min:
									overtime_factor += overtime_mins * i.factor
								elif overtime_mins > i.to_min :
									overtime_factor += i.to_min * i.factor
									overtime_mins -= i.to_min
						else :
							# calculate based on Overtime Law

							if attendance_role.evening_overtime_start and attendance_role.morning_overtime_start and attendance_role.evening_overtime_end and attendance_role.morning_overtime_end :
								morning_start = attendance_role.morning_overtime_start
								morning_end = attendance_role.morning_overtime_end
								morning_factor = attendance_role.morning_overtime_factor
								evening_factor = attendance_role.evening_overtime_factor

								IN = to_timedelta(str(doc.shift_actual_start.time()))
								OUT = to_timedelta(str(doc.shift_actual_end.time()))

								morning_overtime = 0
								evening_overtime = 0
								# OUT + Late OUT
								# IN - Early IN

								if doc.late_out.seconds > 0:
									to_time = OUT + doc.late_out
									x,y = self.get_overtime_rule_period(morning_start,morning_end,OUT,to_time)
									morning_overtime += x
									evening_overtime += y

								if attendance_role.calculate_early_in :
									if doc.early_in.seconds > 0:
										from_time  = IN -  doc.early_in
										x, y = self.get_overtime_rule_period(morning_start, morning_end, from_time, IN)
										morning_overtime += x
										evening_overtime += y



								overtime_factor = (morning_overtime * morning_factor) + (evening_overtime * evening_factor)


		elif attendance_role.type == "Daily" and attendance_role.working_type == "Target Hours":
				if attendance_role.total_working_hours_per_day:
					total = timedelta (hours=attendance_role.total_working_hours_per_day)
					if total < doc.total_wrking_hours :
						doc.overtime_mins =  doc.total_wrking_hours - total


		# frappe.msgprint(str(overtime_factor))
		doc.overtime_factor = overtime_factor or 0
		return  doc
	def get_overtime_rule_period (self,morning_start,morning_end,from_time,to_time):
		morning_overtime = min(morning_end, to_time) - max(morning_start, from_time)
		if morning_overtime < timedelta(minutes=0):
			morning_overtime = timedelta(minutes=0)
		evening_overtime = to_time - from_time - morning_overtime

		return (morning_overtime.seconds/60 ,  evening_overtime.seconds/60)

	def calculate_less_time(self,doc,attendance_role):

		doc.less_time = doc.early_out
		less_time_factor = 0
		less_time_penality = 0
		if attendance_role.enable_less_time_factor_penality:
			if attendance_role.type == "Daily" and attendance_role.working_type == "Shift":
				mins = doc.early_out.seconds / 60
				less_time_factor = 0
				less_time_penality = 0
				if  attendance_role.less_rules :

					for i in attendance_role.less_rules :
						if i.from_min <= mins <= i.to_min:
							less_time_factor += mins * i.factor
						elif mins > i.to_min:
							less_time_factor += i.to_min * i.factor
							mins -= i.to_min
				elif attendance_role.less_time_factor :
					less_time_factor = mins * attendance_role.less_time_factor


			if attendance_role.enable_less_time_penalty:
				if  getattr(attendance_role,'less_penalty_factor_rules',None) :
						perviuos = frappe.db.sql("""
						select SUM(ifnull(early_exit,0))+1 as count  from `tabAttendance`
							where employee = '{employee}'
							  and date(attendance_date) between date('{from_date}') and date('{to_date}')
							  and early_exit = 1
						""".format(employee=doc.employee, from_date=self.payroll_start_date, to_date=doc.date))[0][0] or 1

						if perviuos > len(attendance_role.less_penalty_factor_rules):
							less_time_penality = attendance_role.less_penalty_factor_rules[-1].factor
						else:
							# frappe.msgprint(int(perviuos) - 1)
							# frappe.msgprint(int(perviuos))
							less_time_penality = attendance_role.less_penalty_factor_rules[int(perviuos) - 1].factor



				else:
					less_time_penality = attendance_role.less_time_penalty_factor
		doc.less_time_penalty = less_time_penality
		doc.less_time_factor = less_time_factor
		return doc
	def calculate_leave_factor(self,doc, half_day=0):
		if doc.leave_type:
			leave_type = frappe.get_doc("Leave Type",doc.leave_type)
			factor = 0
			if leave_type.is_ppl or leave_type.is_lwp :
				if leave_type.is_ppl :
					factor = leave_type.fraction_of_daily_salary_per_leave
				elif leave_type.is_lwp:
					factor = 1
				if half_day :
					factor *= frappe.db.get_single_value ("Payroll Settings",daily_wages_fraction_for_half_day) or 0.5
			doc.leave_factor = factor
		return doc




	def check_daily_workers (self):

		employees_sql = """
		select e.name  , rule.name as attendance_rule from `tabAttendance Rule` rule
		inner join tabEmployee e on e.attendance_rule = rule.name
		where rule.docstatus <> 2 and daily_workers = 1
		and e.status = 'Active'
		and e.company = '{company}'
		""".format(company=self.company)
		employees = frappe.db.sql(employees_sql,as_dict=1)
		for emp in employees:
			sql = """
							select log.employee ,SUM(case when log.status = "Absent" then 1 else 0 end) as AbsentDays 
						 ,SUM(case when log.status = "Present"  then 1 else 0 end) as working_days 
						 ,SUM(case when log.status = "Present" and log.weekend = 1  then 1 else 0 end) as taken_days 
						 ,SUM(case when log.status = "Weekend"  then 1 else 0 end) as weekend_days 
			     			  from `tabAttendance` log
							Left Join tabEmployee e on e.name = log.employee
							where date( log.attendance_date) between  date('{start_date}') and date('{end_date}')
							and e.name = '{employee}'
							group by  employee
							;
						""".format(employee = emp.name, start_date=self.payroll_start_date, end_date=self.payroll_end_date)
			# frappe.msgprint(sql)
			attendance = frappe.db.sql(sql, as_dict=1)
			if attendance :
				absent_days = attendance [0].AbsentDays or 0
				actual_working_days = attendance [0].working_days or 0
				weekend_days = attendance [0].weekend_days or 0
				attendance_rule = frappe.get_doc("Attendance Rule",emp.attendance_rule)
				working_days  = attendance_rule.working_days or 0
				taken_days = attendance[0].taken_days or 0
				against_weekend  = attendance_rule.against_weekend or 0
				if against_weekend and working_days :
					total_deserved_weekend =  int(against_weekend * ( actual_working_days /working_days)) or 0
					if total_deserved_weekend :
						days = abs(total_deserved_weekend - weekend_days - taken_days)
						calculated_days = []
						sql = """
										select attendance_date from tabAttendance log  
										where log.status = 'Absent' and log.weekend <> 1 and log.holiday <> 1
										and log.employee = '{employee}'
										and date( log.attendance_date) between  date('{start_date}') and date('{end_date}')
										order by attendance_date desc
									  """.format(employee=emp.name, start_date=self.payroll_start_date,
												 end_date=self.payroll_end_date)
						calculated_days = frappe.db.sql(sql, as_dict=1)

						if total_deserved_weekend > absent_days :

							sql = """
									select attendance_date from tabAttendance log  
									where log.status = 'Present' and log.weekend <> 1 and log.holiday <> 1
									and log.employee = '{employee}'
									and date( log.attendance_date) between  date('{start_date}') and date('{end_date}')
									order by attendance_date desc
								  """.format(employee=emp.name, start_date=self.payroll_start_date,
											 end_date=self.payroll_end_date)
							calculated_days.extend(frappe.db.sql(sql, as_dict=1))




						for row in calculated_days:
							if days > 0:
								self.calculate(emp.name,row.attendance_date , flag=1)
								days -= 1


	def overtime_to_leave_balance(self,employee,attendance_rule,amount):

		last_doc = frappe.db.get_value('Leave Allocation', {"attendance_calculation": self.name, "employee": employee.name},['name'], as_dict=1)
		if last_doc:
			doc = frappe.get_doc("Leave Allocation",last_doc.name)
			doc.cancel()
		leave_type = employee.leave_type or \
					 frappe.db.get_value("Leave Type", {'is_compensatory': 1}, 'name')

		if not leave_type:
			frappe.msgprint(_("Please Set Leave Type in Employee {}:{} to convert Leave Balance".format(employee.name,
																										employee.employee_name)),
							indicator='red')
			return
		if amount:
			daily_working_hours = attendance_rule.total_working_hours_per_day
			amount = round(amount/daily_working_hours, 1)
			if employee.approach_to == 'Lower 0.5' :
				amount = int(amount / 0.5)*0.5
			elif employee.approach_to == 'Bigger 0.5' :
				x = 0.5 if amount % 0.5 > 0 else 0
				amount = (int(amount / 0.5) * 0.5) + x

			month = employee.available_period_in_monthes or 12
			alloc = frappe.new_doc("Leave Allocation")
			alloc.naming_series = 'HR-LAL-.YYYY.-'
			alloc.attendance_calculation = self.name
			alloc.leave_type = leave_type
			alloc.employee = employee.name
			alloc.new_leaves_allocated = amount
			alloc.from_date = self.payroll_effect_date
			alloc.from_date = datetime.strptime(str(alloc.from_date) , '%Y-%m-%d' ).date()
			alloc.to_date = alloc.from_date + relativedelta(months=month)
			alloc.save()
			alloc.submit()

	def post_attendance(self, conditions=""):

		# self.validate ()
		if not self.validate_payroll_period():
			frappe.throw(_("Payroll Period Is closed"))
		self.delete_Additional_salary()

		if self.payroll_start_date and self.payroll_end_date:
			self.check_daily_workers()
			sql = """
				select log.employee ,
							SUM(case when log.status = "Absent" then 1 else 0 end) as AbsentDays ,
							SUM(case when log.status = "Absent"
								and DATE_SUB(log.attendance_date, INTERVAL 1 DAY) not in
								(
									select t.attendance_date from tabAttendance t where t.status = 'Absent' and t.docstatus = 1 and t.employee= log.employee
									and t.attendance_date = DATE_SUB(log.attendance_date, INTERVAL 1 DAY)
									and t.attendance_date between  date('{start_date}') and date('{end_date}') 
								)
								then 1 else 0 end) as cont_AbsentDays
							,
							SUM(case when log.status = "Hold" then 1 else 0 end) as HoldingDays ,
					   SUM(case when log.status = "Present" and log.holiday = 1 then 1 else 0 end) as working_on_holiday ,
					   sec_to_time( SUM(case when ifnull(late_entry,1) = 1 then time_to_sec(late_in) else 0  end ) ) as late_in ,
						sec_to_time( SUM( case when ifnull(early_exit,1) = 1 then time_to_sec(less_time) else 0  end  ) ) as early_out ,
					   sec_to_time( SUM(time_to_sec(early_in) ) ) as early_in ,
						sec_to_time( SUM(time_to_sec(overtime_out) ) ) as late_out ,
					   ifnull(SUM(case when ifnull(late_entry,1) = 1 then (TIME_TO_SEC(late_factor)/60) end),0) as late_factor ,
					   ifnull(SUM(case when log.status = "Present" and log.holiday <> 1 and log.weekend <> 1 and log.calculate_overtime = 1 then TIME_TO_SEC(overtime_factor) * 60 end),0) as normal_overtime_factor ,
					   ifnull(SUM(case when log.status = "Present" and log.holiday = 1 and log.calculate_overtime = 1 then TIME_TO_SEC(overtime_factor) * 60 end),0) as holiday_overtime_factor
					 , ifnull(SUM(case when log.status = "Present" and log.weekend =1  and log.calculate_overtime = 1 then TIME_TO_SEC(overtime_factor) * 60 end),0) as weekend_overtime_factor ,
					   ifnull(SUM(TIME_TO_SEC(overtime_mins)/60),0) as overtime_mins , 
					   ifnull(SUM(case when ifnull(early_exit,1) = 1 then (less_time_factor/60) end ),0) as less_time_factor ,
					   ifnull(SUM(case when ifnull(early_exit,1) = 1 then (less_time_penalty) end ),0) as less_time_penalty ,
					   ifnull(SUM(working_hours),0) as total_wrking_hours ,
					   ifnull(SUM(shift_working_hours),0) as total_shift_working_hours ,
						ifnull(SUM(case when ifnull(late_entry,1) = 1 then  late_penality end ),0) as late_penality,
					   ifnull(SUM(case when ifnull(forget_fingerprint,1) = 1 and fingerprint_type = "IN" then 1 else 0 end ),0) as forget_fingerprint_in,
					   ifnull(SUM(case when ifnull(forget_fingerprint,1) and fingerprint_type = "Out" then 1 else 0 end ),0) as forget_fingerprint_out,
					   ifnull(SUM(case when ifnull(forget_fingerprint,1)  then fingerprint_factor else 0 end ),0) as fingerprint_factor
				from `tabAttendance` log
				INNER Join tabEmployee e on e.name = log.employee
				where date( log.attendance_date) between  date('{start_date}') and date('{end_date}') 
				/*and  log.docstatus = 0 and  log.is_calculated = 0*/


				and e.company = '{company}'
				{conditions}

				group by  log.employee
				;
			""".format(company=self.company, start_date=self.payroll_start_date, end_date=self.payroll_end_date,
					   conditions=conditions)

			# Employee Leaves Sql Query

			leaves_sql = """
				select  log.employee , sum(log.leave_factor) as leave_factor ,log.leave_type , type.salary_component from tabAttendance log
				inner join `tabLeave Type` type on type.name = log.leave_type and (type.is_lwp or type.is_ppl) and type.salary_component is not null
				INNER Join tabEmployee e on e.name = log.employee
				where date( log.attendance_date) between  date('{start_date}') and date('{end_date}') 
				/*and  log.docstatus = 0 and  log.is_calculated = 0*/


				and e.company = '{company}'
				{conditions}

				group by   log.employee , log.leave_type
				;
			""".format(company=self.company, start_date=self.payroll_start_date, end_date=self.payroll_end_date,
					   conditions=conditions)

			attendances = frappe.db.sql(sql, as_dict=1)
			# frappe.msgprint(leaves_sql)
			leaves = frappe.db.sql(leaves_sql, as_dict=1) or []
			if attendances:
				for attendance in attendances:

					employee = frappe.get_doc("Employee", attendance.employee)
					if employee.attendance_rule:
						attendance_role = frappe.get_doc("Attendance Rule", employee.attendance_rule)
						# active_salary_structure = get_assigned_salary_structure (employee.name , self.payroll_effect_date ) or None
						# if active_salary_structure :
						# 	self._salary_structure_doc = frappe.get_doc('Salary Structure Assignment', active_salary_structure)
						# if getattr(self, '_salary_structure_doc', None) :
						# total_hourly_salary = 0
						# for item in self._salary_structure_doc.get(
						# 		"earnings"):  # if not (len(self.get("earnings")) or len(self.get("deductions"))):
						# 	salary_compnent = frappe.get_doc("Salary Component", item.salary_component)
						# 	if salary_compnent:
						# 		if salary_compnent.consider_in_hour_rate and salary_compnent.type == "Earning" and item.amount:
						# 			total_hourly_salary += item.amount
						#
						total_working_days = attendance_role.total_working_days_per_month
						total_working_hours_per_day = attendance_role.total_working_hours_per_day
						total_working_hours_per_month = attendance_role.total_working_hours_per_month

						# self.daily_rate = total_hourly_salary / (total_working_days)
						self.payroll_start_date = datetime.strptime(str(self.payroll_start_date), '%Y-%m-%d').date()
						self.payroll_end_date = datetime.strptime(str(self.payroll_end_date), '%Y-%m-%d').date()
						days = (self.payroll_end_date-self.payroll_start_date).days +1
						# days = days if days >= 30 else 30
						self.hour_rate = 1/(attendance.total_shift_working_hours / days)
						# frappe.msgprint(str(self.hour_rate))
						# Overtime
						if attendance_role.enable_overtime and employee.enable_overtime:

							overtime_salary_component = attendance_role.overtime_salary_component
							weekend_overtime_salary_component = attendance_role.overtime_in_weekend_salary_component
							holiday_overtime_salary_component = attendance_role.overtime_in_holiday_salary_component
							present_overtime_amount = 0
							holiday_overtime_amount = 0
							weekend_overtime_amount = 0
							overtime_leave_amount = 0
							if attendance_role.working_type == "Shift" and attendance_role.type == "Daily":
								if employee.calculate_overtime == 'Money':
									# overtime_factor = int(attendance.AbsentDays) * self.daily_rate
									if attendance_role.max_overtime_hours_per_month:
										if attendance_role.max_overtime_hours_per_month < (
												attendance.normal_overtime_factor / 60):
											attendance.normal_overtime_factor = attendance_role.max_overtime_hours_per_month * 60
									if not attendance_role.normal_overtime_to_leave_balance:
										present_overtime_amount = (attendance.normal_overtime_factor / 60)    * self.hour_rate
									else:
										overtime_leave_amount += (attendance.normal_overtime_factor / 60) or 0

									if not attendance_role.holiday_overtime_to_leave_balance:
										holiday_overtime_amount = (
													attendance.holiday_overtime_factor / 60)   * self.hour_rate
									else:
										overtime_leave_amount += (attendance.holiday_overtime_factor / 60) or 0

									if not attendance_role.weekend_overtime_to_leave_balance:
										weekend_overtime_amount = (
													attendance.weekend_overtime_factor / 60)   * self.hour_rate
									else:
										overtime_leave_amount += (attendance.weekend_overtime_factor / 60) or 0

									self.overtime_to_leave_balance(employee, attendance_role, overtime_leave_amount)
									if present_overtime_amount and overtime_salary_component:
										desc = _('Normal Overtime value : {} '.format(
											str(timedelta(minutes=attendance.normal_overtime_factor))))
										self.submit_Additional_salary(employee.name, overtime_salary_component,
																	  present_overtime_amount, desc, "Normal Overtime")
									if holiday_overtime_amount and holiday_overtime_salary_component:
										desc = _('Holiday Overtime value : {} '.format(
											str(timedelta(minutes=attendance.holiday_overtime_factor))))
										self.submit_Additional_salary(employee.name, holiday_overtime_salary_component,
																	  holiday_overtime_amount, desc, "Holiday Overtime")
									if weekend_overtime_amount and weekend_overtime_salary_component:
										desc = _('Weekend Overtime value : {} '.format(
											str(timedelta(minutes=attendance.weekend_overtime_factor))))
										self.submit_Additional_salary(employee.name, weekend_overtime_salary_component,
																	  weekend_overtime_amount, desc, "Weekend Overtime")

								elif employee.calculate_overtime == 'Leave Balance':
									overtime_leave_amount += (attendance.normal_overtime_factor / 60) or 0
									overtime_leave_amount += (attendance.holiday_overtime_factor / 60) or 0
									overtime_leave_amount += (attendance.weekend_overtime_factor / 60) or 0
									self.overtime_to_leave_balance(employee, attendance_role, overtime_leave_amount)

							elif attendance_role.working_type == "Target Hours":
								overtime_factor = 0
								if attendance_role.type == "Monthly":
									if attendance_role.total_working_hours_per_month:
										total = attendance_role.total_working_hours_per_month
										if attendance.total_wrking_hours > total:
											overtime_factor = (attendance.total_wrking_hours - total) * attendance_role.morning_overtime_factor

								elif attendance_role.type == "Daily":
									overtime_factor = (attendance.overtime_mins / 60) * attendance_role.morning_overtime_factor
								if employee.calculate_overtime == 'Money':
									present_overtime_amount = overtime_factor  # * self.hour_rate
									if present_overtime_amount and overtime_salary_component:
										desc = _('Normal Overtime value : {} '.format(
											str(timedelta(minutes=attendance.normal_overtime_factor_))))
										self.submit_Additional_salary(employee.name, overtime_salary_component,
																	  present_overtime_amount, desc, "Normal Overtime")
								elif employee.calculate_overtime == 'Leave Balance':
									overtime_leave_amount = overtime_factor
									self.overtime_to_leave_balance(employee, attendance_role, overtime_leave_amount)

						# less time
						if attendance_role.enable_less_time_factor_penality:
							less_amount = 0
							less_penalty_amount = 0
							less_salary_compnent = attendance_role.less_time_salary_component or None
							less_penalty_salary_compnent = attendance_role.less_time_penalty_salary_component or None
							less_time = attendance.less_time_factor
							less_time_penalty = attendance.less_time_penalty

							if attendance_role.working_type == "Shift":

								# less_factor = float(attendance_role.less_time_factor) * float(less_time )

								less_amount = less_time   * self.hour_rate
								less_penalty_amount = less_time_penalty  # * self.daily_rate

							elif attendance_role.working_type == "Target Hours":
								if attendance_role.total_working_hours_per_month:
									total = attendance_role.total_working_hours_per_month
									if attendance.total_wrking_hours < total:
										less_time = (total - attendance.total_wrking_hours)
										less_factor = float(less_time) * float(attendance_role.less_time_factor)
										less_amount = less_factor  # * self.hour_rate
							if less_amount and less_salary_compnent:
								desc = _("Less Time : {}".format(timedelta(hours=less_time)))
								self.submit_Additional_salary(employee.name, less_salary_compnent, less_amount, desc,
															  "Less Time")

							if less_penalty_amount and less_penalty_salary_compnent:
								desc = _("Less Time Penality : {}".format(timedelta(hours=less_time)))
								self.submit_Additional_salary(employee.name, less_penalty_salary_compnent,
															  less_penalty_amount, desc, "Less Time Penality")

						# Delays
						if attendance_role.enable_late_penality:
							early_out_Hours = (attendance.early_out.seconds) / 3600
							late_in_Hours = (attendance.late_in.seconds) / 3600
							# delays_factor =  ((early_out_Hours* early_out_rate)/total_working_hours_per_day)

							# delays_amount = delays_factor * self.daily_rate
							penality_amount = 0
							late_amount = 0
							penality_factor = 0
							late_factor = 0
							# frappe.msgprint(str(attendance.late_factor))
							if attendance_role.working_type == "Shift":
								if attendance_role.type == "Daily":
									penality_amount = (attendance.late_penality) or 0
									# late_factor = attendance.late_factor * (attendance_role.late_penalty_factor_by_date or 0)  /60
									late_factor = attendance.late_factor / 60
									late_amount = (late_factor * self.hour_rate) or 0


								elif attendance_role.type == "Monthly":

									late_minutes = (attendance.late_in.seconds / 60) or 0
									penality = None
									for i in attendance_role.late_role_table:
										if i.from_min <= late_minutes:
											penality = i

									if penality:

										penality_factor = penality.level_onefactor * penality.factor
										penality_amount = (penality_factor) or 0

										late_factor = 0
										if penality.add_deduction:
											if penality.deduction_factor:
												late_factor = (penality.deduction_factor * attendance_role.late_penalty_factor_by_date) or 0
											else:
												late_factor = ((attendance.late_in.seconds / 60) * attendance_role.late_penalty_factor_by_date) or 0
										late_amount = late_factor   * self.daily_rate

							if attendance_role.salary_componat_for_late and late_amount:
								desc = _('Delays : {} '.format(str(timedelta(hours=late_factor))))
								self.submit_Additional_salary(employee.name, attendance_role.salary_componat_for_late,
															  late_amount, desc, 'Delays')

							if attendance_role.salary_component_for_late_penalty and penality_amount:
								desc = _('Delays Penality:  {} '.format(str(timedelta(days=penality_factor))))
								self.submit_Additional_salary(employee.name,
															  attendance_role.salary_component_for_late_penalty,
															  penality_amount, desc, 'Delays Penality')

						# forget finger print
						if attendance_role.enable_fingerprint_penality:
							fingerprint_factor = attendance.fingerprint_factor or 0
							fingerprint_amount = (fingerprint_factor) or 0
							# fingerprint_factor_out = attendance_role.fingerprint_forgetten_out_penality or 0
							# fingerprint_amount += (fingerprint_factor_out * attendance.forget_fingerprint_out * self.daily_rate) or 0
							if attendance_role.fingerprint_forgetten_penlaity_salary_component and fingerprint_amount:
								desc = _(
									'Fingerprint IN forgetten times: {} '.format(str(attendance.fingerprint_factor_in)))
								desc += '\n' + _(
									'Fingerprint OUT forgetten times: '.format(str(attendance.forget_fingerprint_out)))
								self.submit_Additional_salary(employee.name,
															  attendance_role.fingerprint_forgetten_penlaity_salary_component,
															  fingerprint_amount, desc, 'Fingerprint Penality')

						# Absents Days
						if attendance_role.enable_absent_penality:
							absent_rate = attendance_role.absent_rate or 0
							absents_salary_component = attendance_role.absent__component
							abset_penalty_component = attendance_role.abset_penalty_component

							if attendance_role.absent_rules:
								absent_rule = frappe.get_doc("Absent Rules", attendance_role.absent_rules)
								if absent_rule.senario == 'Deduction from Salary':
									self.absent_days = int(attendance.AbsentDays)
									absent_rate = 0
									absent_penality_rate = 0
									flag = 1
									if absent_rule.ruletemplate:
										penality_absent_days = self.absent_days

										for i in range(1, self.absent_days + 1):
											if len(absent_rule.ruletemplate) >= i:
												absent_rate += absent_rule.ruletemplate[i - 1].deduction
												absent_penality_rate += absent_rule.ruletemplate[i - 1].penality
											else:
												absent_rate += absent_rule.ruletemplate[-1].deduction
												absent_penality_rate += absent_rule.ruletemplate[-1].penality

										if attendance_role.continuous_absent_penality:
											penality_absent_days = int(attendance.cont_AbsentDays)
											absent_penality_rate = 0
											for i in range(1, penality_absent_days + 1):
												if len(absent_rule.ruletemplate) >= i:
													absent_penality_rate += absent_rule.ruletemplate[i - 1].penality
												else:
													absent_penality_rate += absent_rule.ruletemplate[-1].penality

									absent_amount = absent_rate  # * self.daily_rate
									absent_penality_amount = absent_penality_rate  # *   self.daily_rate
									if absent_amount and absents_salary_component:
										desc = _('Absent Days Factor: '.format(str(timedelta(days=absent_rate))))
										self.submit_Additional_salary(employee.name, absents_salary_component,
																	  absent_amount, desc, 'Absent Days')
									if absent_penality_amount and abset_penalty_component:
										desc = _('Absent Days Penaliteies: '.format(
											str(timedelta(days=absent_penality_rate))))
										self.submit_Additional_salary(employee.name, abset_penalty_component,
																	  absent_penality_amount, desc,
																	  'Absent Days Penaliteies')
						# Holding Days
						if attendance.HoldingDays and attendance_role.hold_salary_component:
							hold_amount = attendance.HoldingDays  # * self.daily_rate
							if hold_amount:
								desc = _(
									'Hold Days: '.format(str(timedelta(days=attendance.HoldingDays))))
								self.submit_Additional_salary(employee.name, attendance_role.hold_salary_component,
															  hold_amount, desc,
															  'Hold Days')

						# Leaves
						employee_leaves = [i for i in leaves if i.employee == attendance.employee] or []
						for leave in employee_leaves:
							leave_amount = (leave.leave_factor or 0)  # * self.daily_rate
							if leave_amount and leave.salary_component:
								desc = _(
									'{} Leaves Day:  {}'.format(leave.leave_type,
																str(timedelta(days=leave.leave_factor))))

								self.submit_Additional_salary(employee.name, leave.salary_component,
															  leave_amount, desc,
															  str(leave.leave_type))

					# else :
					# 	frappe.msgprint(_('Employee {} has no Active Salary Structure'.format(employee.employee_name)))
					else:
						frappe.msgprint(_('Employee {} has no Attendance Rule'.format(employee.employee_name)))

	def submit_Additional_salary(self, employee, salary_component, amount, desc , attendance_flag):
		last_doc = frappe.db.get_value('Additional Salary', { "salary_component":salary_component , "employee":employee ,"attendance_calculation" : self.name , "attendance_flag":attendance_flag},  ['name', 'salary_slip'], as_dict=1)
		if last_doc :
			salary_slip = last_doc.salary_slip
			last_doc = last_doc.name
		if not last_doc or (last_doc and (not salary_slip)) :
				component = frappe.get_doc("Salary Component", salary_component)
					# Data for update_component_row
				doc = frappe.new_doc("Additional Salary")
				doc.amount = amount
				doc.salary_component = salary_component
				doc.employee = employee
				doc.overwrite_salary_structure_amount = 0
				doc.is_addditional_salary = 1
				doc.company = self.company
				# doc.amount_based_on_formula = 0
				doc.type = component.type
				doc.payroll_date = self.payroll_effect_date
				# doc.description = desc
				doc.attendance_calculation = self.name
				doc.attendance_flag = attendance_flag
				doc.save()
				doc.submit()
		else:
			# doc = frappe.get_doc("Additional Salary",last_doc)
			# doc.amount += amount
			# doc.save()
			frappe.msgprint(_("Employee {employee} has this Additional Salary {name} before <br>Please delete Additional Salary {name} it first ".format(employee=employee , name=last_doc)))


	def delete_Additional_salary(self):
		frappe.db.sql("""delete from `tabAdditional Salary` where  attendance_calculation= '{name}' and salary_slip is null """.format(name=self.name))

	def validate(self):
		pass

	def validate_payroll_period(self):
			sql = frappe.db.sql(
				""" select p.name from  `tabPayroll Period` p where p.name = '{name}' and p.is_closed <> 1""".format(
					name=self.payroll_period), as_dict=1)
			return 1 if sql else 0
	# def enqueue_calculate (self):
	# 	# return
	# 	total_days = (self.to_date - self.from_date).days +1
	# 	count = 0
	# 	for employee in self.employees :
	# 		permissions = frappe.db.sql("""
	# 		select permission.name , date(permission.date) as date , type.code , SUBTIME (permission.to_time,permission.from_time) as Duration
	# 		from tabPermission permission inner join `tabPermission Type` type on type.name = permission.permission_type
	# 		where permission.docstatus = 1 and status = "Completed"
	# 		and date(date) between date('{from_date}') and date('{to_date}') and employee = '{employee}'
	# 		group by  permission.name ;
	# 	"""
	# 	.format(from_date = self.payroll_start_date,to_date=self.payroll_end_date , employee = employee),as_dict=1) or []
	# 		missions = frappe.db.sql("""
	# 					select * from `tabMission` where docstatus = 1
	# 					and date(tabMission.date)  between date('{from_date}') and date('{to_date}')  and employee = '{employee}'
	# 					order by start_time asc ,  end_time asc
	# 						""".format(from_date = self.payroll_start_date,to_date=self.payroll_end_date , employee = employee), as_dict=1) or []
	# 		businessTrips = frappe.db.sql("""
	# 				select * from `tabBusiness Trip` where docstatus = 1
	# 				 and (
	# 				 	(date(from_date)  between date('{from_date}') and date('{to_date}'))
	# 				 or (date(to_date)  between date('{from_date}') and date('{to_date}'))
	# 				 or (date(to_date) >= date('{to_date}') and date(from_date) <=date('{from_date}'))
	# 				 )
	# 				and employee = '{employee}'
	# 				""".format(from_date = self.payroll_start_date,to_date=self.payroll_end_date , employee=employee), as_dict=1) or []
	#
	#
	# 		index = str(self.employees.index(employee) + 1)
	# 		employee = employee [0]
	# 		self.emp = frappe.get_doc("Employee", employee)
	# 		count += 1
	# 		day = datetime.strptime(str(self.from_date), '%Y-%m-%d').date()
	# 		frappe.publish_progress(count * 100 / total_days, title=_(footer))
	# 		self.used_permission_balance =sum([(x.Duration or 0) for x in permissions])
	# 		self.permission_taken_minutes = 0
	# 		while day <= self.to_date:
	# 			footer = " Calculate for {} {} / {} Employee".format(str(employee), index ,
	# 												  str(len(self.employees)))
	#
	# 			# frappe.publish_realtime('update_progress_attendance_calculation', {
	# 			# 	'progress': count,
	# 			# 	'total': total_days,
	# 			# 	'footer': _(footer)
	# 			# })
	#
	# 			self.calculate(employee=employee, day=day , missions=missions , businessTrips=businessTrips , permissions=permissions )
	# 			day += timedelta(days=1)
	# 			count += 1

def enqueue_calculate(self, employees):
		# return
		self.employees = employees
		total_days = (self.to_date - self.from_date).days + 1
		count = 0

		for employee in self.employees:
			index = str(self.employees.index(employee) + 1)
			employee = employee[0]
			self.emp = frappe.get_doc("Employee", employee)
			count += 1
			footer = " Calculate for {} {} / {} Employee".format(str(employee), index,
																 str(len(self.employees)))
			day = datetime.strptime(str(self.from_date), '%Y-%m-%d').date()
			# frappe.publish_progress(count * 100 / len(employees), title=_(footer))
			frappe.publish_realtime('update_progress_attendance_calculation', {
				'progress': count,
				'total': len(self.employees),
				'footer': _(footer)
			})
			# permissions = []
			permissions = frappe.db.sql("""
						select permission.name , date(permission.date) as date , type.code , SUBTIME (permission.to_time,permission.from_time) as Duration
						from tabPermission permission inner join `tabPermission Type` type on type.name = permission.permission_type
						where permission.docstatus = 1 and status = "Completed"
						and date(date) between date('{from_date}') and date('{to_date}') and employee = '{employee}'
						group by  permission.name ;
					"""
				.format(from_date = self.payroll_start_date,to_date=self.payroll_end_date , employee = employee),as_dict=1) or []


			missions = frappe.db.sql("""
									select * from `tabMission` where docstatus = 1
									and date(tabMission.date)  between date('{from_date}') and date('{to_date}')  and employee = '{employee}'
									order by start_time asc ,  end_time asc
										""".format(from_date=self.payroll_start_date, to_date=self.payroll_end_date,
												   employee=employee), as_dict=1) or []
			businessTrips = frappe.db.sql("""
								select * from `tabBusiness Trip` where docstatus = 1
								 and (
								 	(date(from_date)  between date('{from_date}') and date('{to_date}'))
								 or (date(to_date)  between date('{from_date}') and date('{to_date}'))
								 or (date(to_date) >= date('{to_date}') and date(from_date) <=date('{from_date}'))
								 )
								and employee = '{employee}'
								""".format(from_date=self.payroll_start_date, to_date=self.payroll_end_date,
										   employee=employee), as_dict=1) or []

			self.used_permission_balance = sum([(int(x.Duration.seconds / 60) or 0) for x in permissions])
			self.permission_taken_minutes = 0
			while day <= self.to_date:
				# frappe.publish_progress(count * 100 / total_days, title=_(footer))

				# frappe.publish_realtime('update_progress_attendance_calculation', {
				# 	'progress': count,
				# 	'total': total_days,
				# 	'footer': _(footer)
				# })

				self.calculate(employee=employee, day=day , missions=[] , businessTrips=[] , permissions=[] )
				day += timedelta(days=1)


def get_employee_shift_backup(employee, for_date, consider_default_shift=False, next_shift_direction=None):
	"""Returns a Shift Type for the given employee on the given date. (excluding the holidays)

	:param employee: Employee for which shift is required.
	:param for_date: Date on which shift are required
	:param consider_default_shift: If set to true, default shift is taken when no shift assignment is found.
	:param next_shift_direction: One of: None, 'forward', 'reverse'. Direction to look for next shift if shift not found on given date.
	"""
	shift_type_name = None
	shift_assignment_details = frappe.db.get_value('Shift Assignment', {'employee':employee, 'start_date':('<=', for_date), 'docstatus': '1', 'status': "Active"}, ['shift_type', 'end_date','working_hours','start_time','end_time'])
	working_hours = 0
	start_time = None
	end_time = None
	if shift_assignment_details:
		shift_type_name = shift_assignment_details[0]
		working_hours = shift_assignment_details[2] or 0
		start_time = shift_assignment_details[3]
		end_time = shift_assignment_details[4]

		# if end_date present means that shift is over after end_date else it is a ongoing shift.
		if shift_assignment_details[1] and for_date >= shift_assignment_details[1] :
			shift_type_name = None

	if not shift_type_name and consider_default_shift:
		shift_type_name = frappe.db.get_value('Employee', employee, 'default_shift')
		if not shift_type_name:
			company = frappe.db.get_value('Employee', employee, 'company')
			if company :
				shift_type_name = frappe.db.get_value('Company', company, 'default_shift')
	return get_shift_details(shift_type_name, for_date , working_hours,start_time,end_time)



def get_employee_shift(employee, for_date, consider_default_shift=False, next_shift_direction=None):
	"""Returns a Shift Type for the given employee on the given date. (excluding the holidays)

	:param employee: Employee for which shift is required.
	:param for_date: Date on which shift are required
	:param consider_default_shift: If set to true, default shift is taken when no shift assignment is found.
	:param next_shift_direction: One of: None, 'forward', 'reverse'. Direction to look for next shift if shift not found on given date.
	"""
	shift_type_name = None
	shift_assignment_details = frappe.db.get_value('Shift Assignment', {'employee':employee, 'start_date':('<=', for_date), 'docstatus': '1', 'status': "Active"}, ['shift_type', 'end_date','working_hours','start_time','end_time'])
	working_hours = 0
	start_time = None
	end_time = None
	if shift_assignment_details:
		shift_type_name = shift_assignment_details[0]
		working_hours = shift_assignment_details[2] or 0
		start_time = shift_assignment_details[3]
		end_time = shift_assignment_details[4]

		# if end_date present means that shift is over after end_date else it is a ongoing shift.
		if shift_assignment_details[1] and for_date >= shift_assignment_details[1] :
			shift_type_name = None

	if not shift_type_name and consider_default_shift:
		shift_type_name = frappe.db.get_value('Employee', employee, 'default_shift')
		if not shift_type_name:
			company = frappe.db.get_value('Employee', employee, 'company')
			if company :
				shift_type_name = frappe.db.get_value('Company', company, 'default_shift')
	return get_shift_details(shift_type_name, for_date , working_hours,start_time,end_time)





def get_shift_details(shift_type_name, for_date, working_hours = 0 , start_time = None , end_time = None):
	"""Returns Shift Details which contain some additional information as described below.
	'shift_details' contains the following keys:
		'shift_type' - Object of DocType Shift Type,
		'start_datetime' - Date and Time of shift start on given date,
		'end_datetime' - Date and Time of shift end on given date,
		'actual_start' - datetime of shift start after adding 'begin_check_in_before_shift_start_time',
		'actual_end' - datetime of shift end after adding 'allow_check_out_after_shift_end_time'(None is returned if this is zero)

	:param shift_type_name: shift type name for which shift_details is required.
	:param for_date: Date on which shift_details are required
	"""
	if not shift_type_name:
		return None
	shift_type = frappe.get_doc('Shift Type', shift_type_name)
	if not working_hours:
		working_hours = shift_type.default_working_hours or 0

	custom_start_end = shift_type.custom_start_end
	is_flexible_hours = shift_type.is_flexible_hours
	start_datetime = datetime.combine(for_date, datetime.min.time()) + shift_type.start_time
	for_date = for_date + timedelta(days=1) if shift_type.start_time > shift_type.end_time else for_date
	end_datetime = datetime.combine(for_date, datetime.min.time()) + shift_type.end_time
	actual_start = start_datetime - timedelta(minutes=shift_type.begin_check_in_before_shift_start_time)
	actual_end = end_datetime + timedelta(minutes=shift_type.allow_check_out_after_shift_end_time)

	return frappe._dict({
		'shift_type': shift_type,
		'start_datetime': start_datetime,
		'end_datetime': end_datetime,
		'actual_start': actual_start,
		'actual_end': actual_end,
		'working_hours':working_hours,
		'is_flexible_hours':is_flexible_hours,
		'custom_start_end':custom_start_end,
		'start_time':start_time or to_timedelta(str(start_datetime.time())),
		'end_time':end_time or  to_timedelta(str(end_datetime.time()))
	})





def get_assigned_salary_structure(employee, on_date):
		if not employee or not on_date:
			return None
		salary_structure = frappe.db.sql("""
			select name from `tabSalary Structure Assignment`
			where employee=%(employee)s
			and docstatus = 1
			and %(on_date)s >= from_date order by from_date desc limit 1""", {
			'employee': employee,
			'on_date': on_date,
		})
		return None  if not salary_structure else salary_structure[0][0]




