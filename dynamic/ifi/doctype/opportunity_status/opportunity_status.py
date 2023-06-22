# Copyright (c) 2022, Dynamic and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class OpportunityStatus(Document):

	@frappe.whitelist()
	def test(self):
		doc_events = frappe.get_doc_hooks()
		print('\n\n\n',doc_events,'\n\n')
		raise TypeError("Only integers are allowed") 
		print('\n\n\n','test---->','\n\n')

	pass
