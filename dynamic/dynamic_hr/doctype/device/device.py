# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
import sys
import os
from zk import ZK, const
from datetime import datetime
from datetime import timedelta
from frappe.model.naming import make_autoname
import time
from erpnext.hr.doctype.shift_type.shift_type import process_auto_attendance_for_all_shifts
  

class Device(Document):
    @frappe.whitelist()
    def get_attendance(self):
        # frappe.msgprint(os.path)
        # self.save()
        doc = self
        device_name = self.name
        series = "Log-{}-{}-.#####"
        sql = ""
        if doc:
            if doc.is_active:
                # create ZK instance
                last_log_date = None
                last_connection = datetime.now()
                last_error = None
                conn = None
                miniutes_period = 5
                # device = ZK('192.168.1.201', port=4370, timeout=5, password=0, force_udp=False, ommit_ping=False)

                try:
                    # connect to device
                    tic = time.perf_counter()
                    device = ZK(ip=str(self.ip) or '192.168.1.201', port=int(doc.port),
                                timeout=5, password=int(doc.password),
                                force_udp=False, 	ommit_ping=False
                                )
                    #

                    conn = device.connect()
                    # disable device, this method ensures no activity on the device while the process is run
                    # conn.disable_device()
                    # another commands will be here!
                    # Example: Get All records

                    attendances = device.get_attendance()

                    # attendances = sorted(attendances, key=lambda i: int(i.user_id))
                    # frappe.msgprint(str(attendances))
                    toc = time.perf_counter()
                    # frappe.msgprint(f"Downloaded the tutorial in {toc - tic:0.4f} seconds")
                    tic = time.perf_counter()
                    last_user_log = {}
                    if attendances:
                        old_user = ''
                        old_timestamp = None
                        user = '1'
                        total = len(attendances)
                        count = 0
                        toc = time.perf_counter()
                        # frappe.msgprint(f"Downloaded the tutorial in {toc - tic:0.4f} seconds")
                        tic = time.perf_counter()
                        # for i in attendances:
                        for record in attendances:
                            count += 1
                            frappe.publish_realtime('update_progress_device', {
                                'progress': count,
                                'total': total
                            })
                            if doc.last_log_date:
                                if record.timestamp < datetime.strptime(str(doc.last_log_date), '%Y-%m-%d %H:%M:%S'):
                                    continue

                            user = record.user_id
                            old_timestamp = last_user_log.get(user, None)
                            if old_timestamp:
                                period = record.timestamp - old_timestamp
                                if user == old_user and period <= timedelta(minutes=miniutes_period):
                                    # frappe.msgprint("Continue" + str(record.timestamp))
                                    continue

                            log = frappe.new_doc('Device Log')
                            log.enroll_no = record.user_id
                            log.log_time = record.timestamp
                            log.log_type = "OUT" if str(
                                record.status) == "1" else "IN"
                            log.punch = record.punch
                            log.parent = device_name
                            log.parenttype = 'Device'
                            log.parentfield = 'device_logs'
                            log.device = device_name
                            log.device_name = doc.device_name
                            log.log_date = record.timestamp.date()

                            old_user = user
                            last_user_log[user] = record.timestamp

                            log.name = make_autoname(series.format(
                                log.enroll_no, log.log_time), doctype="Device Log")

                            frappe.db.sql("""insert into `tabDevice Log` (name,enroll_no,log_time,log_type,punch,parent,parenttype,parentfield,device,device_name,log_date,time_log,creation,modified,modified_by,owner)
																			VALUES  ('{name}',{enroll_no},'{log_time}','{log_type}',{punch},'{parent}','Device','device_logs','{device}','{device_name}',date(log_time),time(log_time),CURRENT_TIMESTAMP(),CURRENT_TIMESTAMP(), '{user}','{user}')
															 """.format(name=log.name, enroll_no=log.enroll_no,
                                log_time=log.log_time, log_type=log.log_type,
                                punch=log.punch, parent=device_name, device_name=log.device_name,
                                device=device_name, user=frappe.session.user))

                            last_log_date = record.timestamp
                        frappe.db.commit()

                    else:
                        frappe.msgprint(_("No Data Found After {}".format(
                            doc.last_log_date)), indicator='blue')
                    toc = time.perf_counter()
                    # frappe.msgprint(f"Downloaded the tutorial in {toc - tic:0.4f} seconds")
                    # Test Voice: Say Thank You
                    # conn.test_voice()
                # re-enable device after all commands already executed
                # conn.enable_device()
                    frappe.msgprint(_("Operation Successfully"))
                except Exception as e:
                    frappe.msgprint("Process terminate : {}".format(e))
                    # frappe.msgprint("Process terminate : {}".format(sql))
                    last_error = e
                finally:
                    if conn:
                        conn.disconnect()
                    # conn.enable_device()
                    try:
                        # document = frappe.get_doc('Device', device_name)
                        if last_log_date:
                            self.last_log_date = last_log_date
                        if last_connection:
                            self.last_connection = last_connection
                        if last_error:
                            self.last_error = last_error

                        self.save()
                        create_employee_checkin()
                        if self.auto_calculate_attendance:
                            calculate_attendance()
                    except:
                        pass


@frappe.whitelist()
def map_employees():
    frappe.db.sql("""update `tabDevice Log` log set employee = (select name from `tabEmployee` where attendance_device_id = log.enroll_no) ,
	employee_name = (select employee_name from `tabEmployee` where attendance_device_id = log.enroll_no),
	log_date = date(log_time),
	shift = (select shift from `tabDevice` where name = log.device),
	time_log = time(log_time) 
	where ifnull(employee,'') = '' or ifnull(employee_name,'') = ''
	
	 """)


# @frappe.whitelist()
# def create_employee_checkin(names=None):
# 	map_employees()
# 	sql = """
# 	Insert Into `tabEmployee Checkin` (name , employee , time , log_type,device_log,device_id,creation,modified,owner)
# 	(select name , employee , time_log , log_type,name,device,creation,modified,owner from 
# 	`tabDevice Log` where employee is not null
# 	and  name not in (select device_log from `tabEmployee Checkin` where device_log is not null));
# 	"""
# 	# frappe.msgprint(sql)
# 	frappe.db.sql(sql)
# 	frappe.db.commit()
# 	frappe.msgprint(_("Operation Successfully"))


@frappe.whitelist()
def create_employee_checkin(names=None):
	map_employees()
	# sql = """
	# Insert Into `tabEmployee Checkin` (name , employee , time , log_type,device_log,device_id,creation,modified,owner)
	# (select name , employee , time_log , log_type,name,device,creation,modified,owner from 
	# `tabDevice Log` where employee is not null
	# and  name not in (select device_log from `tabEmployee Checkin` where device_log is not null));
	# """
	sql = """
	select name , employee , log_time , log_type,name,device,creation,modified,owner from 
	`tabDevice Log` where employee is not null
	and  name not in (
		select device_log from `tabEmployee Checkin` where device_log is not null
		);
	"""
	# frappe.msgprint(sql)
	logs = frappe.db.sql(sql,as_dict=1) or []
	for log in logs :
		try :
			checkin = frappe.new_doc("Employee Checkin")
			checkin.employee = log.employee
			checkin.time = log.log_time
			checkin.log_type = log.log_type
			checkin.device_log = log.name
			checkin.device_id = log.device
			checkin.save()
		except Exception as e :
			pass
			# frappe.msgprint(_("Error While create Employee {employee} checkin {log_time} {e}").format(
			# 	employee=log.employee,
			# 	log_time=log.log_time,
			# 	e=str(e)
			# ))
	if len(logs) > 0 :
		frappe.msgprint(_("Operation Successfully"))
	else :
		frappe.msgprint(_("There is no new logs"))



# @frappe.whitelist()
# def calculate_attendance():
#     attendances = frappe.db.sql(""" 
# 		select calc.name from `tabAttendance Calculation` calc
# 		inner join `tabPayroll Period` period on calc.payroll_period = period.name
# 		where period.docstatus < 2 and ifnull(is_closed,0) = 0
#         and calc.docstatus < 2
#          """, as_dict=1)
#     if not attendances or len(attendances) == 0:
#         # if 1 :
#         payroll_period = frappe.db.sql("""
# 			select period.name from `tabPayroll Period` period
# 			where period.docstatus < 2 and ifnull(is_closed,0) = 0
# 		""", as_dict=1)
#         if payroll_period and len(payroll_period) != 0:
#             for i in payroll_period:
#                 try:
#                     period = frappe.get_doc("Payroll Period", i.name)
#                     doc = frappe.new_doc("Attendance Calculation")
#                     doc.payroll_period = period.name
#                     doc.company = period.company
#                     doc.from_date = period.attendance_start_date
#                     doc.to_date = period.attendance_end_date
#                     doc.payroll_effect_date = period.attendance_end_date

#                     doc.insert()
#                     doc.Calculate_attendance()
#                 except Exception as e:
#                     frappe.msgprint(str(e))
#     else:
#         for i in attendances:
#             doc = frappe.get_doc("Attendance Calculation", i.name)
#             try:

#                 doc.Calculate_attendance()
#             except Exception as e:
#                 frappe.msgprint(str(e))

@frappe.whitelist()
def calculate_attendance():
	process_auto_attendance_for_all_shifts()


@frappe.whitelist()
def get_device_status():
    # frappe.msgprint('hh')
    devices = frappe.get_all(
        "Device", fields=["name", "ip", "port", "password", "status"]) or []
    connected = []
    disconnected = []
    for device in devices:
        # device = frappe.get_doc('Device',i.name)		#
        device.status = 'Disconnected'
        zk_device = ZK(ip=str(device.ip), port=int(device.port or '4370'),
                       timeout=2, password=int(device.password or '0'),
                       force_udp=False, ommit_ping=False
                       )
        try:
            zk_device.connect()
        except Exception as e:
            pass
            # frappe.msgprint(str(e))
            # frappe.msgprint(device.name)
        finally:
            # device.status = 'Disconnected' if not zk_device.is_connect else 'Connected'
            if zk_device.is_connect:
                connected.append("'{}'".format(device.name))
            else:
                disconnected.append("'{}'".format(device.name))

            # device.save()
            try:
                zk_device.disconnect()
            except Exception as e:
                pass
    if len(connected) > 0:
        sql = """
					update tabDevice set status = 'Connected'
					where name in ({l})
					""".format(l=','.join(connected))
        # frappe.msgprint(sql)
        frappe.db.sql(sql)
        frappe.db.commit()
    if len(disconnected) > 0:
        sql = """
					update tabDevice set status = 'Disconnected'
					where name in ({l})
					""".format(l=','.join(disconnected))
        # frappe.msgprint(sql)
        frappe.db.sql(sql)
        frappe.db.commit()
