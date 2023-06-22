# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from dynamic.dynamic_hr.doctype.device.device import map_employees
class DeviceLog(Document):
	# def after_insert (self):
	# 	# self.map_employees()
	# 	# frappe.msgprint("DDDDONNNNNNNE")
	# 	pass
	@frappe.whitelist()
	def map_employees(self):
		map_employees()
		# frappe.db.sql("""update `tabDevice Log` log set employee = (select name from `tabEmployee` where attendance_device_id = log.enroll_no)
		# 	where ifnull(employee,'') = '' """)




