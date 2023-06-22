# Copyright (c) 2022, Dynamic and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from dynamic.api import generate_item_code
class ItemRequest(Document):
	

	def on_submit(self):
		item = frappe.new_doc("Item")
		item.item_code      = generate_item_code(self.item_group) #self.item_code
		item.item_name      = self.item_name
		item.item_group     = self.item_group
		item.stock_uom      = self.stock_uom
		# item.valuation_rate = self.valuation_rate
		item.standard_rate  = self.standard_rate	
		item.color          = self.color
		item.size           = self.size
		item.specs  = self.specification
		item.cutting_type   = self.cutting_type
		item.uoms           = self.uoms
		item.save(ignore_permissions=True)

	
	@frappe.whitelist()
	def can_approve_item(self,*args, **kwargs):
		role = frappe.db.get_single_value("Terra Seeting","item_approver")
		return role 