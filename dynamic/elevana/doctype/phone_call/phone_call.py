# Copyright (c) 2023, Dynamic and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc


class PhoneCall(Document):
	def validate(self):
		self.validate_customer()
		self.validate_lead()

	def validate_customer(self):
		if not self.customer :
			sql = f"""
					select
						DISTINCT link.link_name ,
						link.link_title
					from
						tabContact contact
					inner join `tabDynamic Link` link on
						link.parent = contact.name
					left join `tabContact Phone` contact_phone on
						contact_phone.parent = contact.name
					where
						link.link_doctype = 'Customer'
						and 
						(
						contact.phone like '%{self.phone_number}%'
							or contact.mobile_no like '%{self.phone_number}%'
							or contact_phone.phone like '%{self.phone_number}%'
						)
					order by
						contact .creation desc
					limit 1
			"""
			result = frappe.db.sql(sql ,as_dict =1)
			if result :
				result = result[0]
				customer = frappe.get_doc("Customer" ,result.link_name )
				self.customer =  customer.name
				self.customer_name =  customer.customer_name
				self.territory =  customer.territory
				self.customer_group =  customer.customer_group
				self.lead =  customer.lead_name
				# self.db_set('customer' , customer.name)
				# self.db_set('customer_name' , customer.customer_name)
				# self.db_set('territory' , customer.territory)
				# self.db_set('customer_group' , customer.customer_group)
				# self.db_set('customer_group' , customer.customer_group)
			

	def validate_lead(self):
		if not self.lead :
			sql = f"""
					select
						lead.name ,
						lead.lead_name ,
						lead.territory
					from
						tabLead lead
					where
											
						lead.phone like '%{self.phone_number}%'
						or lead.mobile_no like '%{self.phone_number}%'
					order by
						lead .creation desc
					limit 1
			"""
			result = frappe.db.sql(sql ,as_dict =1)
			if result :
				lead = result[0]
				self.db_set('lead' , lead.name)
				self.customer_name = self.customer_name or lead.lead_name
				self.territory = self.territory or lead.territory
				# self.db_set('customer_name' , self.customer_name or lead.lead_name)
				# self.db_set('territory' , self.territory or lead.territory)
			


	def before_insert(self):
		# if not self.user :
		self.user = self.user or frappe.session.user



	def on_trash(self):
		if self.customer:
			customer = frappe.get_doc("Customer", self.customer)
			customer.db_set("ref_docname" , '')
			customer.db_set("ref_doctype" , '')


@frappe.whitelist()
def create_customer(source_name, target_doc=None, ignore_permissions=False):
	source = frappe.get_doc("Phone Call", source_name)

	def postprocess(source, target):
		set_missing_values(source, target)

	def set_missing_values(source, target):
		target.flags.ignore_permissions = True
		target.update({'ref_doctype': source.doctype})
		target.update({'ref_docname': source.name})

	customer = get_mapped_doc("Phone Call", source_name, {
		"Phone Call": {
			"doctype": "Customer",
			"field_map": {
				"customer_name": "customer_name",
				"territory": "territory",
				"customer_group": "customer_group",
			},
		},
	}, target_doc, postprocess, ignore_permissions=ignore_permissions)

	customer.save()
	source.db_set("customer", customer.name)
	source.db_set("customer_name", customer.customer_name)
	source.db_set("territory", customer.territory)
	source.db_set("customer_group", customer.customer_group)
	source.db_set("lead", customer.lead_name)

	contact = frappe.new_doc("Contact")
	contact.first_name = customer.customer_name
	contact.phone = source.phone_number
	contact.mobile_no = source.phone_number
	contact.set("phone_nos", [])
	contact.append("phone_nos", {
		"phone": source.phone_number
	})
	contact.set("links", [])
	contact.append("links", {
		"link_doctype": customer.doctype,
		"link_name": customer.name,
		"link_title": customer.customer_name
	})
	contact.append("links", {
		"link_doctype": source.doctype,
		"link_name": source.name,
		"link_title": source.customer_name
	})
	contact.save()

	customer.db_set('customer_primary_contact', contact.name)

	return customer


@frappe.whitelist()
def create_lead(source_name, target_doc=None, ignore_permissions=False):
	source = frappe.get_doc("Phone Call", source_name)

	def postprocess(source, target):
		set_missing_values(source, target)

	def set_missing_values(source, target):
		target.flags.ignore_permissions = True
		# target.update({'ref_doctype': source.doctype})
		# target.update({'ref_docname': source.name})
		target.update({'mobile_no': source.phone_number})

	lead = get_mapped_doc("Phone Call", source_name, {
		"Phone Call": {
			"doctype": "Lead",
			"field_map": {
				"customer_name": "lead_name",
				"territory": "territory",
				"phone_number": "phone",

			},
		},
	}, target_doc, postprocess, ignore_permissions=ignore_permissions)

	lead.save()
	source.db_set("customer_name", lead.lead_name)
	source.db_set("territory", lead.territory)
	source.db_set("lead", lead.name)

	return lead
