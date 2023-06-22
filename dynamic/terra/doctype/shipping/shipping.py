# Copyright (c) 2022, Dynamic and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, nowdate, today
from erpnext import get_default_company

class Shipping(Document):
	def create_shipping_journal_entry(self):
		doc = frappe.get_doc("Mode of Payment",self.mode_of_payment)
		company = get_default_company()
		mode_of_payment_account = None
		
		for acc in doc.accounts:
			if acc.company == company:
				mode_of_payment_account = acc.default_account

		if not mode_of_payment_account:
			frappe.throw(_("You must set deafult account for mode of payment '%s'"%self.mode_of_payment))

		if self.type == "Recive":
			self.create_journal_entry(mode_of_payment_account,self.shipping_account,self.amount)
		elif self.type == "Pay":
			self.create_journal_entry(self.shipping_account,mode_of_payment_account,self.amount)
	def on_submit(self):
		self.create_shipping_journal_entry()
		

	def create_journal_entry(self,debit_account,credit_account,amount):
		print(f"------------------- {self.sales_order}---------------------------")
		company = get_default_company()
		je = frappe.new_doc("Journal Entry")
		je.posting_date = nowdate()
		je.company = company

		#debit
		je.append("accounts", {
				"account": debit_account,
				"debit_in_account_currency": amount,
				"debit_in_company_currency": amount,
				"cost_center": self.cost_center
			})
		#credit
		je.append("accounts", {
					"account": credit_account,
					"credit_in_account_currency": amount,
					"credit_in_company_currency": amount,
					"cost_center": self.cost_center
					
				})
		# print("accountss ===================> ",je.accounts[1].get("reference_name"))
		je.save()
		je.submit()
		self.journal_entry = je.name
		je.save()

	

	def vallidate_mode_of_payment_account(self):
		doc = frappe.get_doc("Mode of Payment",self.mode_of_payment)
		if len(doc.accounts) == 0:
			frappe.throw(_("Please set default Cash or Bank account in Mode of Payment Wire Transfer"))

	def validate(self):
		self.vallidate_mode_of_payment_account()

	
