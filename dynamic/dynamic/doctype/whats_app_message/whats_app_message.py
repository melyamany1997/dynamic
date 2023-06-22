# Copyright (c) 2022, Dynamic and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
import json
import requests
import sys
import base64


#check If number is KSA Linked With Moyate Domain 
DOMAINS = frappe.get_active_domains()
class WhatsAppMessage(Document):
	def get_whats_app_data(self) :
		whats_obj = frappe.get_doc("WhatsApp" , self.fromm)
		INSTANCE_URL = whats_obj.instance_url
		PRODUCT_ID = whats_obj.product_id
		API_TOKEN = whats_obj.api_token 
		PHONE_ID = whats_obj.phone_id
		#validate Status 
		if whats_obj.status == "Deactivate" :
			frappe.throw(_("Profile is Not Active "))
		if self.mobil_number :
			#Send Whats Message
			url = INSTANCE_URL + f"/{PRODUCT_ID}/{PHONE_ID}/sendMessage"
			payload = { "message" : str(whats_obj.messgae) ,
						"to_number" : f"{self.mobil_number}",
						"type": str(whats_obj.messgae_type), }

			headers = {
			"Content-Type": "application/json",
			"x-maytapi-key": API_TOKEN,
							}
			r = requests.request('POST', url, headers=headers, data=json.dumps(payload))
			tjson = r.json()
			#frappe.throw(str(tjson))
			self.message = whats_obj.messgae
			self.status  =str( r.json())
	def get_contact_number(self):
		linked_contact = frappe.db.sql(f""" 
		SELECT a.parent as contact , b.phone as phone FROM `tabDynamic Link`  a
		INNER Join `tabContact Phone` b 
		ON b.parent = a.parent
		WHERE a.parenttype ="Contact" AND a.link_doctype = "Customer" AND a.link_name='{self.customer}'
		GROUP BY a.parent
		""",as_dict = True)
		if len(linked_contact) == 0 :
			frappe.msgprint(str(_("No Contact Found ")))
		if len(linked_contact) > 0 :
			#frappe.throw(str(linked_contact))
		    #set Data
			self.contact = linked_contact[-1].get("contact")
			self.mobil_number = linked_contact[-1].get("phone")
			if  'Moyate' in DOMAINS:  
				self.mobil_number = "+966" + str(linked_contact[-1].get("phone"))[1::]
				
			self.get_whats_app_data()

	def validate(self):
		if not self.fromm :
			frappe.throw(_("Please Select Wahts App  API Account"))
		if not self.customer :
				frappe.throw(_("Please Select Customer Account"))
		self.get_contact_number()