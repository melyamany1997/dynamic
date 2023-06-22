# Copyright (c) 2023, Dynamic and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class test_ifi(Document):
	def set_indicator(self):
		"""Set indicator for portal"""
		if self.salary < 100 :
			self.indicator_color = "orange"
			self.indicator_title = _("less than 100")

		elif self.per_billed == 100 :
			self.indicator_color = "green"
			self.indicator_title = _(" equal 100 ")

		else:
			self.indicator_color = "blue"
			self.indicator_title = _("more than 100")
