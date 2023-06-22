# Copyright (c) 2022, Dynamic and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class UpdatedInvoices(Document):
	def validate(self) :
		if self.old_name and self.new_name :
			self.status = "Competed"
		else :
			self.status = "Invalid"
