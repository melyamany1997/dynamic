# Copyright (c) 2023, Dynamic and contributors
# For license information, please see license.txt

import frappe
from random import randint
from frappe.model.document import Document


class CouponGroup(Document):

	def before_submit(self):
		self.generate_codes()

	def generate_codes(self):
		codes = []
		self.set("coupon_codes",[])
		while len(codes) < self.no_of_codes :
			new_code = random_with_n_digits()
			exist = frappe.db.get_value("Coupon Code" , {"coupon_code" : new_code} , 'name')
			if not exist and new_code not in codes :
				codes.append(new_code)
				coupon = frappe.new_doc("Coupon Code")
				coupon.coupon_name = self.coupon_name + " - " + new_code
				coupon.coupon_code = new_code
				coupon.coupon_type = self.coupon_type
				coupon.pricing_rule = self.pricing_rule
				coupon.valid_from = self.valid_from
				coupon.valid_upto = self.valid_upto
				coupon.maximum_use = self.maximum_use
				coupon.description = self.description
				coupon.ref_doctype = self.doctype
				coupon.ref_docname = self.name
				coupon.save()
				self.append('coupon_codes',{
					"coupon":coupon.name,
					"coupon_code":coupon.coupon_code
				})
		
		# for code in codes :
		# 	coupon = frappe.new_doc("Coupon Code")
		# 	coupon.coupon_name = self.coupon_name + " - " + code
		# 	coupon.coupon_code = code
		# 	coupon.coupon_type = self.coupon_type
		# 	coupon.pricing_rule = self.pricing_rule
		# 	coupon.valid_from = self.valid_from
		# 	coupon.valid_upto = self.valid_upto
		# 	coupon.maximum_use = self.maximum_use
		# 	coupon.description = self.description
		# 	coupon.ref_doctype = self.doctype
		# 	coupon.ref_docname = self.name
		# 	coupon.save()
		# 	self.append('coupon_codes',{
		# 		"coupon":coupon.name,
		# 		"coupon_code":coupon.coupon_code
		# 	})
			
			




def random_with_n_digits(n=10):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return str(randint(range_start, range_end))
