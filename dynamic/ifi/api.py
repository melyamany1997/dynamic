

from erpnext.controllers.accounts_controller import get_advance_journal_entries, get_advance_payment_entries
import frappe
from frappe import _
from frappe.utils import getdate
from datetime import datetime
from frappe.utils.background_jobs import enqueue
from frappe.model.mapper import get_mapped_doc
from erpnext.selling.doctype.quotation.quotation import _make_customer
from frappe.utils import flt, getdate, nowdate
from erpnext.selling.doctype.sales_order.sales_order import make_purchase_order, is_product_bundle, set_delivery_date
from six import string_types
import json
from frappe.core.doctype.communication.email import make
from frappe.desk.form.load import get_attachments
from frappe.utils import get_url
from erpnext.accounts.party import get_party_account
from erpnext.crm.doctype.lead.lead import _set_missing_values
from erpnext.accounts.party import get_party_account_currency
from erpnext.setup.utils import get_exchange_rate
from erpnext.stock.doctype.item.item import get_item_defaults, get_last_purchase_details
from erpnext.setup.doctype.item_group.item_group import get_item_group_defaults
from frappe.model.utils import get_fetch_values
from frappe.utils import add_days, cint, cstr, flt, get_link_to_form, getdate, nowdate, strip_html

from frappe.contacts.doctype.address.address import get_company_address


DOMAINS = frappe.get_active_domains()


@frappe.whitelist()
def opportunity_notifiy(self, *args, **kwargs):
	if "IFI" in DOMAINS:
		get_alert_dict(self)
		# reciever
		# email_quotation(self, *args, **kwargs)
		# supplier_rfq_mail(self)
	if "Terra" in DOMAINS :
		if self.opportunity_from == "Customer" :
			self.customer = self.party_name
	

@frappe.whitelist()
def quotation_send_email_cc(self, *args, **kwargs):
	if 'IFI' in DOMAINS:
		email_group = frappe.db.get_single_value(
			'IFI Settings', 'email_group_quotation')
		email_id = frappe.db.get_value('Customer', self.party_name, 'email_id')
		cc_emails = []
		if email_group:
			cc_emails = frappe.db.get_list('Email Group Member', filters={
										   'email_group': email_group}, fields=['email'], pluck='email')
		if email_id:
			email_args = {
				"recipients": email_id,
				"cc": cc_emails if len(cc_emails) else [],
				"message": _("Quotation Appointement"),
				"subject": 'Quotation Valid Till Date'.format(self.valid_till),
				"message": "test quotation",
				"attachments": [frappe.attach_print(self.doctype, self.name, file_name=self.name)],
				"reference_doctype": self.doctype,
				"reference_name": self.name
			}
			enqueue(method=frappe.sendmail, queue="short",
					timeout=300, now=True, is_async=True, **email_args)
		else:
			frappe.msgprint(
				_("{0}: Customer  Has No Mail, hence email not sent"))


@frappe.whitelist()
def lead_contact_by_email(self, *args, **kwargs):
	if "IFI" in DOMAINS:
		if self.phone_no1 and len(self.phone_no1) != 11:
			frappe.throw(_("phone number must be 11 digits"))
			
		receiver = self.contact_by
		if receiver:
			email_args = {
				"recipients": [receiver],
				"message": _("Lead Date"),
				"subject": 'Lead Next Contatct Date :'.format(self.contact_date),
				# "message": self.get_message(),
				# "attachments": [frappe.attach_print(self.doctype, self.name, file_name=self.name)],
				"reference_doctype": self.doctype,
				"reference_name": self.name
			}
			enqueue(method=frappe.sendmail, queue="short",
					timeout=300, now=True, is_async=True, **email_args)
			get_alert_dict_lead(self)
		else:
			frappe.msgprint(
				_("{0}: Next Contatct By User Has No Mail, hence email not sent").format(self.contact_by))

@frappe.whitelist()
def get_alert_dict_lead(self):
	owner_name = self.contact_by
	customer_name = self.lead_name
	contact_date = self.contact_date
	notif_doc = frappe.new_doc('Notification Log')
	notif_doc.subject = f"{owner_name} Contact to {customer_name} at {contact_date}"
	notif_doc.for_user = owner_name
	notif_doc.type = "Mention"
	notif_doc.document_type = self.doctype
	notif_doc.document_name = self.name
	notif_doc.from_user = frappe.session.user
	notif_doc.insert(ignore_permissions=True)

@frappe.whitelist()
def daily_opportunity_notify(self, *args, **kwargs):
	if 'IFI' in DOMAINS:
		# date_now =getdate()
		today = datetime.now().strftime('%Y-%m-%d')
		sql = f"""
			select name,contact_by,customer_name,contact_date,'Opportunity' as doctype from tabOpportunity to2 
			where CAST(contact_date AS DATE) ='{today}'
		"""
		data = frappe.db.sql(sql, as_dict=1)
		for opprt in data:
			get_alert_dict(opprt)


@frappe.whitelist()
def get_alert_dict(self):
	owner_name = self.contact_by
	customer_name = self.customer_name
	contact_date = self.contact_date
	notif_doc = frappe.new_doc('Notification Log')
	notif_doc.subject = f"{owner_name} Contact to {customer_name} at {contact_date}"
	notif_doc.for_user = owner_name
	notif_doc.type = "Alert"
	notif_doc.document_type = self.doctype
	notif_doc.document_name = self.name
	notif_doc.from_user = frappe.session.user
	notif_doc.insert(ignore_permissions=True)


# @frappe.whitelist()
# def email_quotation(self, *args, **kwargs):
# 	receiver = frappe.db.get_value("User", self.contact_by, "email")
# 	if receiver:
# 		email_args = {
# 			"recipients": [receiver],
# 			"message": _("Quotation Appointement"),
# 			"subject": 'Quotation Appointement At Date'.format(self.contact_date),
# 			# "message": self.get_message(),
# 			# "attachments": [frappe.attach_print(self.doctype, self.name, file_name=self.name)],
# 			"reference_doctype": self.doctype,
# 			"reference_name": self.name
# 		}
# 		enqueue(method=frappe.sendmail, queue="short",
# 				timeout=300, now=True, is_async=True, **email_args)
# 	else:
# 		frappe.msgprint(
# 			_("{0}: Next Contatct By User Has No Mail, hence email not sent").format(self.contact_by))


# @frappe.whitelist()
# def email_supplier_invoice(self, *args, **kwargs):
# 	receiver = frappe.db.get_value("Supplier", self.supplier, "email_id")
# 	if receiver:
# 		email_args = {
# 			"recipients": [receiver],
# 			"message": _("Please GET Notify "),
# 			"subject": 'Purchase Receipt - IN'.format(self.posting_date),
# 			# "attachments": [frappe.attach_print(self.doctype, self.name, file_name=self.name)],
# 			"reference_doctype": self.doctype,
# 			"reference_name": self.name
# 		}
# 		enqueue(method=frappe.sendmail, queue="short",
# 				timeout=300, now=True, is_async=True, **email_args)
# 	else:
# 		frappe.msgprint(
# 			_("{0}: Supplier ha no mail, hence email not sent").format(self.supplier))


@frappe.whitelist()
def create_furniture_installation_order(source_name, target_doc=None):
	doclist = get_mapped_doc("Sales Order", source_name, {
		"Sales Order": {
			"doctype": "Installations Furniture",
			"field_map": {
				"name": "sales_order",
						"customer": "customer"
			},
			"validation": {
				"docstatus": ["=", 1]
			}
		},
		"Sales Order Item": {
			"doctype": "Installation Furniture Item",
			"field_map": {
				"name": "ref_name",
				"item_code": "item_code",
				"item_name": "item_name",
				"qty": "qty",
				"rate": "rate",
				"amount": "amount",
				"delivery_date": "delivery_date",
			}
		}
	}, target_doc)
	so_doc =frappe.get_doc("Sales Order",source_name)
	cust_addresss = frappe.db.get_value('Customer',so_doc.customer,'url')
	doclist.url = cust_addresss
	return doclist


@frappe.whitelist()
def make_sales_order(source_name, target_doc=None):
	if 'IFI' in DOMAINS:
		quotation = frappe.db.get_value(
			"Quotation", source_name, ["transaction_date", "valid_till"], as_dict=1
		)
		if quotation.valid_till and (
				quotation.valid_till < quotation.transaction_date or quotation.valid_till < getdate(
					nowdate())
		):
			frappe.throw(_("Validity period of this quotation has ended."))
		return _make_sales_order(source_name, target_doc)


def _make_sales_order(source_name, target_doc=None, ignore_permissions=False):
	customer = _make_customer(source_name, ignore_permissions)

	def set_missing_values(source, target):
		if customer:
			target.customer = customer.name
			target.customer_name = customer.customer_name
		if source.referral_sales_partner:
			target.sales_partner = source.referral_sales_partner
			target.commission_rate = frappe.get_value(
				"Sales Partner", source.referral_sales_partner, "commission_rate"
			)
		target.flags.ignore_permissions = ignore_permissions
		target.run_method("set_missing_values")
		target.run_method("calculate_taxes_and_totals")
		# Get the advance paid Journal Entries in Sales Invoice Advance
		if target.get("allocate_advances_automatically"):
			target.set_advances()

	def update_item(obj, target, source_parent):
		target.stock_qty = flt(obj.qty) * flt(obj.conversion_factor)

		if obj.against_blanket_order:
			target.against_blanket_order = obj.against_blanket_order
			target.blanket_order = obj.blanket_order
			target.blanket_order_rate = obj.blanket_order_rate

	doclist = get_mapped_doc(
		"Quotation",
		source_name,
		{
			"Quotation": {
				"doctype": "Sales Order",
				"field_map": {
					"crean": "crean",
					"crean_amount": "crean_amount",
					"allocate_advances_automatically": "allocate_advances_automatically",
					"order_type": "order_type"
				},
				"validation":
					{"docstatus": ["=", 1]}
			},
			"Quotation Item": {
				"doctype": "Sales Order Item",
				"field_map": {"parent": "prevdoc_docname"},
					"postprocess": update_item,
			},
			"Sales Taxes and Charges": {"doctype": "Sales Taxes and Charges", "add_if_empty": True},
			"Sales Team": {"doctype": "Sales Team", "add_if_empty": True},
			"Payment Schedule": {"doctype": "Payment Schedule", "add_if_empty": True},
			"Sales Invoice Advance": {"doctype": "Sales Invoice Advance", "add_if_empty": True},
		},
		target_doc,
		set_missing_values,
		ignore_permissions=ignore_permissions,
	)

	# postprocess: fetch shipping address, set missing values
	doclist.set_onload("ignore_price_list", True)

	return doclist


@frappe.whitelist()
def override_make_purchase_order(source_name, selected_items=None, target_doc=None):
	if "IFI" in DOMAINS:
		if not selected_items:
			return

		if isinstance(selected_items, string_types):
			selected_items = json.loads(selected_items)

		items_to_map = [
			item.get("item_code")
			for item in selected_items
			if item.get("item_code") and item.get("item_code")
		]
		items_to_map = list(set(items_to_map))

		def set_missing_values(source, target):
			target.supplier = ""
			target.apply_discount_on = ""
			target.additional_discount_percentage = 0.0
			target.discount_amount = 0.0
			target.inter_company_order_reference = ""
			target.customer = ""
			target.customer_name = ""
			target.run_method("set_missing_values")
			target.run_method("calculate_taxes_and_totals")

		def update_item(source, target, source_parent):
			target.schedule_date = source.delivery_date
			target.qty = flt(
				source.qty) - (flt(source.ordered_qty) / flt(source.conversion_factor))
			target.stock_qty = flt(source.stock_qty) - flt(source.ordered_qty)
			target.project = source_parent.project

		def update_item_for_packed_item(source, target, source_parent):
			target.qty = flt(source.qty) - flt(source.ordered_qty)

		# po = frappe.get_list("Purchase Order", filters={"sales_order":source_name, "supplier":supplier, "docstatus": ("<", "2")})
		doc = get_mapped_doc(
			"Sales Order",
			source_name,
			{
				"Sales Order": {
					"doctype": "Purchase Order",
					"field_map": {
						"customer": "customer_so",

					},
					"field_no_map": [
						"address_display",
						"shipping_rule",
						"contact_display",
						"contact_mobile",
						"contact_email",
						"contact_person",
						"taxes_and_charges",
						"shipping_address",
						"terms",
					],
					"validation": {"docstatus": ["=", 1]},
				},
				"Sales Order Item": {
					"doctype": "Purchase Order Item",
					"field_map": [
						["name", "sales_order_item"],
						["parent", "sales_order"],
						["stock_uom", "stock_uom"],
						["uom", "uom"],
						["conversion_factor", "conversion_factor"],
						["delivery_date", "schedule_date"],
					],
					"field_no_map": [
						"rate",
						"price_list_rate",
						"item_tax_template",
						"discount_percentage",
						"discount_amount",
						"supplier",
						"pricing_rules",
					],
					"postprocess": update_item,
					"condition": lambda doc: doc.ordered_qty < doc.stock_qty
					and doc.item_code in items_to_map
					and not is_product_bundle(doc.item_code),
				},
				"Packed Item": {
					"doctype": "Purchase Order Item",
					"field_map": [
						["name", "sales_order_packed_item"],
						["parent", "sales_order"],
						["uom", "uom"],
						["conversion_factor", "conversion_factor"],
						["parent_item", "product_bundle"],
						["rate", "rate"],
					],
					"field_no_map": [
						"price_list_rate",
						"item_tax_template",
						"discount_percentage",
						"discount_amount",
						"supplier",
						"pricing_rules",
					],
					"postprocess": update_item_for_packed_item,
					"condition": lambda doc: doc.parent_item in items_to_map,
				},
			},
			target_doc,
			set_missing_values,
		)

		set_delivery_date(doc.items, source_name)

		return doc
	make_purchase_order(source_name, selected_items=None, target_doc=None)
	# print('\n\n\n\n/////*********')
	# print(source_name)


def supplier_rfq_mail(self, preview=False):
	# full_name = get_user_fullname(frappe.session["user"])
	# if full_name == "Guest":
	# 	full_name = "Administrator"

	# send document dict and some important data from suppliers row
	# to render message_for_supplier from any template
	doc_args = self.as_dict()
	doc_args.update({"party": self.party_name, "test": 2222})

	args = {
		"message": frappe.render_template("hello from other side", doc_args),
		"rfq_link": get_link(self),
		"user_fullname": "abanoub moubir full name",
		"supplier_name": self.party_name,
		"supplier_salutation": "Dear Mx.",
	}

	subject = _("Request for Opportunity")
	template = "templates/emails/opportunity.html"
	sender = "abanoubmounir07@gmail.com"
	# frappe.get_template(template).render(args)
	message = "message body for mail ---> %s" % args.get('rfq_link')

	if preview:
		return message

	attachments = get_attachments2(self)

	send_email(self, sender, subject, message, attachments)


def send_email(self, sender, subject, message, attachments):
	make(
		subject=subject,
		content=message,
		recipients="abanoub.mounir9@gmail.com",
		sender=sender,
		attachments=attachments,
		send_email=True,
		doctype=self.doctype,
		name=self.name,
	)["name"]

	frappe.msgprint(_("Email Sent to Supplier {0}").format(self.party_name))


def get_attachments2(self, name=None):
	attachments = [d.name for d in get_attachments(self.doctype, self.name)]
	attachments.append(frappe.attach_print(self.doctype, self.name, doc=self))
	return attachments


def get_link(self):
	# RFQ link for supplier portal
	return get_url("/app/opportunity/" + self.name)


@frappe.whitelist()
def create_new_appointment_ifi(source_name, target_doc=None):
	if 'IFI' in DOMAINS:
		doc = frappe.get_doc("Lead", source_name)
		appointment_doc = frappe.new_doc("Appointment")
		appointment_doc.customer_name = doc.lead_name
		appointment_doc.customer_phone_number = doc.get('phone_no1', '')
		appointment_doc.appointment_with = "Lead"
		appointment_doc.party = doc.name
		appointment_doc.customer_email = doc.email_id
		return appointment_doc


@frappe.whitelist()
def get_events(start, end, filters=None):
	"""Returns events for Gantt / Calendar view rendering.
	frappe
	:param start: Start date-time.
	:param end: End date-time.
	:param filters: Filters (JSON).
	"""
	from erpnext.controllers.queries import get_match_cond
	from frappe.desk.calendar import get_event_conditions
	filters = json.loads(filters)
	# conditions = get_event_conditions("Appointment", filters)
	conditions = get_event_conditions("Appointment", filters)

	events = []
	data = frappe.db.sql("""
		select
			`tabAppointment`.name as name,
			 `tabAppointment`.customer_name as cst,
			  `tabAppointment`.scheduled_time as start,
			 ADDTIME(`tabAppointment`.scheduled_time,'2:00:00') as end,
			 concat(`tabAppointment`.customer_name,'--',`tabAppointment`.scheduled_time )as description
		from
			`tabAppointment`
			where
			(`tabAppointment`.scheduled_time between %(start)s and %(end)s)
			{conditions}
		""".format(conditions=conditions),
		{"start": start, "end": end},
		as_dict=True,
		update={"allDay": 0},
	)

	# for row in data:
	# 	job_card_data = {
	#         "start": row.start,
	#         "planned_end_date": row.end,
	#         "name": row.name,
	#         "subject": row.customer,
	#         "color":'#D3D3D3',
	#     }
	# 	events.append(job_card_data)

	return data


@frappe.whitelist()
def create_action_lead(source_name, target_doc=None):
	doc = frappe.get_doc("Lead", source_name)
	adction = frappe.new_doc("Actions")
	adction.customer_type = 'Lead'
	if not doc.get('contact_date', ''):
		frappe.throw(_('Add Next Contact Date'))
	adction.date = doc.get('contact_date', '').date()
	adction.time = doc.get('contact_date', '').time()
	# adction.party = doc.name
	# adction.customer_email = doc.email_id
	return adction


@frappe.whitelist()
def create_action_cst(source_name, target_doc=None):
	doc = frappe.get_doc("Customer", source_name)
	action = frappe.new_doc("Actions")
	action.customer_type = 'Customer'
	action.customer = doc.get('name', '')
	return action


@frappe.whitelist()
def create_action_opportunity(source_name, target_doc=None):
	doc = frappe.get_doc("Opportunity", source_name)
	action = frappe.new_doc("Actions")
	action.customer_type = 'Opportunity'
	action.customer = doc.get('name', '')
	return action


@frappe.whitelist()
def check_buying_price(self, *args, **kwargs):
	if 'IFI' in DOMAINS:
		if self.buying:
			buying_rate = self.price_list_rate
			if buying_rate > 0.0:
				selling_prices = frappe.db.get_list('Item Price', filters={
													"selling": 1, "item_code": self.item_code}, fields=['name', 'price_list_rate'])
				for price in selling_prices:
					if buying_rate > price.price_list_rate:
						frappe.throw(
							_(f"Item Price {buying_rate} has value more than {price.name} - {price.price_list_rate} "))
		if self.selling:
			selling_rate = self.price_list_rate
			if selling_rate > 0.0:
				buying_prices = frappe.db.get_list('Item Price', filters={
													"buying": 1, "item_code": self.item_code}, fields=['name', 'price_list_rate'])
				for buying_price in buying_prices:
					if selling_rate < buying_price.price_list_rate:
						frappe.throw(
							_(f"Item Price {selling_rate} has value less than {buying_price.name}-{buying_price.price_list_rate} "))



@frappe.whitelist()
def validate_payemnt_entry(doc) :
	if doc.payment_type in ["Pay" , "Internal Transfer"] :
		#validate account balance > 0 :
		if doc.paid_from_account_balance <= 0 :
			frappe.throw(_(f""" No Credit avaliable in Account {doc.paid_from} """))

		# validate account balance equal paid amount 

		if doc.base_paid_amount >   doc.paid_from_account_balance  :
			frappe.throw(_(f"""Account {doc.paid_from} balance is { doc.base_paid_amount} and you try to Transfer {doc.base_paid_amount}"""))

# @frappe.whitelist()
# def send_mail_supplier_ifi_po(self, *args, **kwargs):
# 	if 'IFI' in DOMAINS:
# 		if self.supplier:
# 			email_id = frappe.db.get_value(
# 				'Supplier', self.supplier, 'email_id')
# 			if email_id:
# 				email_args = {
# 					"recipients": email_id,
# 					"message": _("Purchase Order Notify"),
# 					"subject": 'Purchase Order',
# 					"message": "test Purchase Order",
# 					# "attachments": [frappe.attach_print(self.doctype, self.name, file_name=self.name)],
# 					"reference_doctype": self.doctype,
# 					"reference_name": self.name
# 				}
# 				enqueue(method=frappe.sendmail, queue="short",
# 						timeout=300, now=True, is_async=True, **email_args)
# 			else:
# 				frappe.msgprint(
# 					_("{0}:Supplier Has No Mail").format(self.supplier))




@frappe.whitelist()
def reject_quotation_ifi(source_name):
	frappe.db.set_value("Quotation", source_name, "status", "Rejected")
	# try:
	# 	return True
	# except Exception as ex:
	# 	return str(ex)
	# 	print("exception",str(ex))


@frappe.whitelist()
def make_purchase_order_for_default_supplier(source_name, selected_items=None, target_doc=None):
	"""Creates Purchase Order for each Supplier. Returns a list of doc objects."""
	if not selected_items:
		return

	if isinstance(selected_items, string_types):
		selected_items = json.loads(selected_items)

	def set_missing_values(source, target):
		target.supplier = supplier
		target.apply_discount_on = ""
		target.additional_discount_percentage = 0.0
		target.discount_amount = 0.0
		target.inter_company_order_reference = ""

		default_price_list = frappe.get_value(
			"Supplier", supplier, "default_price_list")
		if default_price_list:
			target.buying_price_list = default_price_list

		if any(item.delivered_by_supplier == 1 for item in source.items):
			if source.shipping_address_name:
				target.shipping_address = source.shipping_address_name
				target.shipping_address_display = source.shipping_address
			else:
				target.shipping_address = source.customer_address
				target.shipping_address_display = source.address_display

			target.customer_contact_person = source.contact_person
			target.customer_contact_display = source.contact_display
			target.customer_contact_mobile = source.contact_mobile
			target.customer_contact_email = source.contact_email

		else:
			target.customer = ""
			target.customer_name = ""

		target.run_method("set_missing_values")
		target.run_method("calculate_taxes_and_totals")

	def update_item(source, target, source_parent):
		target.schedule_date = source.delivery_date
		target.qty = flt(source.qty) - (flt(source.ordered_qty) /
										flt(source.conversion_factor))
		target.stock_qty = flt(source.stock_qty) - flt(source.ordered_qty)
		target.project = source_parent.project

	suppliers = [item.get("supplier")
				 for item in selected_items if item.get("supplier")]
	# remove duplicates while preserving order
	suppliers = list(dict.fromkeys(suppliers))

	items_to_map = [item.get("item_code")
					for item in selected_items if item.get("item_code")]
	items_to_map = list(set(items_to_map))

	if not suppliers:
		frappe.throw(
			_("Please set a Supplier against the Items to be considered in the Purchase Order.")
		)

	purchase_orders = []
	for supplier in suppliers:
		doc = get_mapped_doc(
			"Sales Order",
			source_name,
			{
				"Sales Order": {
					"doctype": "Purchase Order",
					"field_no_map": [
						"address_display",
						"contact_display",
						"contact_mobile",
						"contact_email",
						"contact_person",
						"taxes_and_charges",
						"shipping_address",
						"terms",
						"shipping_rule"
					],
					"validation": {"docstatus": ["=", 1]},
				},
				"Sales Order Item": {
					"doctype": "Purchase Order Item",
					"field_map": [
						["name", "sales_order_item"],
						["parent", "sales_order"],
						["stock_uom", "stock_uom"],
						["uom", "uom"],
						["conversion_factor", "conversion_factor"],
						["delivery_date", "schedule_date"],
					],
					"field_no_map": [
						"rate",
						"price_list_rate",
						"item_tax_template",
						"discount_percentage",
						"discount_amount",
						"pricing_rules",
					],
					"postprocess": update_item,
					"condition": lambda doc: doc.ordered_qty < doc.stock_qty
					and doc.supplier == supplier
					and doc.item_code in items_to_map,
				},
				"Sales Taxes and Charges": {
					"doctype": "Purchase Taxes and Charges",
					# "field_map": [
					# 	["charge_type", "charge_type"],
					# 	["account_head", "account_head"],
					# 	["rate", "rate"],
					# 	["amount", "amount"],
					# 	["total", "total"],
					# 	["description", "description"],
					# 	# ["cost_center", "cost_center"],
					# 	# ["cost_center", "cost_center"],
					# ],
				},
			},
			target_doc,
			set_missing_values,
		)

		doc.insert()
		frappe.db.commit()
		purchase_orders.append(doc)

	return purchase_orders


@frappe.whitelist()
def make_purchase_order(source_name, selected_items=None, target_doc=None):
	if not selected_items:
		return

	if isinstance(selected_items, string_types):
		selected_items = json.loads(selected_items)

	items_to_map = [
		item.get("item_code")
		for item in selected_items
		if item.get("item_code") and item.get("item_code")
	]
	items_to_map = list(set(items_to_map))

	def set_missing_values(source, target):
		target.supplier = ""
		target.apply_discount_on = ""
		target.additional_discount_percentage = 0.0
		target.discount_amount = 0.0
		target.inter_company_order_reference = ""
		target.customer = ""
		target.customer_name = ""
		target.run_method("set_missing_values")
		target.run_method("calculate_taxes_and_totals")

	def update_item(source, target, source_parent):
		target.schedule_date = source.delivery_date
		target.qty = flt(source.qty) - (flt(source.ordered_qty) /
										flt(source.conversion_factor))
		target.stock_qty = flt(source.stock_qty) - flt(source.ordered_qty)
		target.project = source_parent.project

	def update_item_for_packed_item(source, target, source_parent):
		target.qty = flt(source.qty) - flt(source.ordered_qty)

	# po = frappe.get_list("Purchase Order", filters={"sales_order":source_name, "supplier":supplier, "docstatus": ("<", "2")})
	doc = get_mapped_doc(
		"Sales Order",
		source_name,
		{
			"Sales Order": {
				"doctype": "Purchase Order",
				"field_no_map": [
					"address_display",
					"contact_display",
					"contact_mobile",
					"contact_email",
					"contact_person",
					"taxes_and_charges",
					"shipping_address",
					"terms",
					"shipping_rule",

				],
				"validation": {"docstatus": ["=", 1]},
			},
			"Sales Order Item": {
				"doctype": "Purchase Order Item",
				"field_map": [
					["name", "sales_order_item"],
					["parent", "sales_order"],
					["stock_uom", "stock_uom"],
					["uom", "uom"],
					["conversion_factor", "conversion_factor"],
					["delivery_date", "schedule_date"],
				],
				"field_no_map": [
					"rate",
					"price_list_rate",
					"item_tax_template",
					"discount_percentage",
					"discount_amount",
					"supplier",
					"pricing_rules",
				],
				"postprocess": update_item,
				"condition": lambda doc: doc.ordered_qty < doc.stock_qty
				and doc.item_code in items_to_map
				and not is_product_bundle(doc.item_code),
			},
			"Sales Taxes and Charges": {
				"doctype": "Purchase Taxes and Charges",
				# "field_map": [
				# 	["charge_type", "charge_type"],
				# 	["account_head", "account_head"],
				# 	["rate", "rate"],
				# 	["amount", "amount"],
				# 	["total", "total"],
				# 	["description", "description"],
				# 	# ["cost_center", "cost_center"],
				# 	# ["cost_center", "cost_center"],
				# ],
			},
			"Packed Item": {
				"doctype": "Purchase Order Item",
				"field_map": [
					["name", "sales_order_packed_item"],
					["parent", "sales_order"],
					["uom", "uom"],
					["conversion_factor", "conversion_factor"],
					["parent_item", "product_bundle"],
					["rate", "rate"],
				],
				"field_no_map": [
					"price_list_rate",
					"item_tax_template",
					"discount_percentage",
					"discount_amount",
					"supplier",
					"pricing_rules",
				],
				"postprocess": update_item_for_packed_item,
				"condition": lambda doc: doc.parent_item in items_to_map,
			},
		},
		target_doc,
		set_missing_values,
	)

	set_delivery_date(doc.items, source_name)

	return doc


@frappe.whitelist()
def get_advanced_so_ifi(doc_name):
	"""Returns list of advances against Account, Party, Reference"""
	self = frappe.get_doc('Sales Order', doc_name)
	res = get_advance_entries(self)
	self.set("advancess", [])
	# print('\n\n\n-->res:',res)
	advance_allocated = 0
	for d in res:
		if d.against_order:
			allocated_amount = flt(d.amount)
			d['allocated_amount'] = allocated_amount
		else:
			if self.get("party_account_currency") == self.company_currency:
				amount = self.get(
					"base_rounded_total") or self.base_grand_total
			else:
				amount = self.get("rounded_total") or self.grand_total

			allocated_amount = min(amount - advance_allocated, d.amount)
			d['allocated_amount'] = allocated_amount
		advance_allocated += flt(allocated_amount)
		

		# self.append("advancess", advance_row)
	# print('\n\n\n-->after update:',res)
	return res



def get_advance_entries(self, include_unallocated=True):
	if self.doctype == "Sales Invoice":
		party_account = self.debit_to
		party_type = "Customer"
		party = self.customer
		amount_field = "credit_in_account_currency"
		order_field = "sales_order"
		order_doctype = "Sales Order"
	elif self.doctype == "Sales Order":
		party_account = get_party_account("Customer", party=self.customer, company=self.company)
		party_type = "Customer"
		party = self.customer
		amount_field = "credit_in_account_currency"
		order_field = "sales_order"
		order_doctype = "Sales Order"
	else:
		party_account = self.credit_to
		party_type = "Supplier"
		party = self.supplier
		amount_field = "debit_in_account_currency"
		order_field = "purchase_order"
		order_doctype = "Purchase Order"

	# print('\n\n-->party_type',party_account)
	# order_list = list(set(d.get(order_field) for d in self.get("items") if d.get(order_field)))
	order_list = [self.name, ]
	journal_entries = get_advance_journal_entries(
		party_type, party, party_account, amount_field, order_doctype, order_list, include_unallocated
	)

	payment_entries = get_advance_payment_entries(
		party_type, party, party_account, order_doctype, order_list, include_unallocated
	)

	res = journal_entries + payment_entries

	return res


@frappe.whitelist()
def send_mail_daily_opportunity_lead():
	send_to_lead()
	send_to_opportunity()

@frappe.whitelist()
def send_to_lead():
	sql = "SELECT q.name,q.contact_date,q.contact_by, 'Lead' as doctype FROM `tabLead` q WHERE q.docstatus=0 AND q.contact_date >= NOW() "
	data = frappe.db.sql(sql,as_dict=1)
	send_mail_opport_and_lead(data)

@frappe.whitelist()
def send_to_opportunity():
	sql = "SELECT q.name,q.contact_date,q.contact_by, 'Opportunity' as doctype FROM `tabOpportunity` q WHERE q.docstatus=0 AND q.contact_date >= NOW()"
	data = frappe.db.sql(sql,as_dict=1)
	send_mail_opport_and_lead(data)


def send_mail_opport_and_lead(data):
	recipients = []
	for row in data:
		if row.contact_by:
			email_args = {
					"recipients": row.contact_by,
					"message": _("Please GET Notify For _Daily_ %s"%row.doctype),
					"subject": 'Contact In {contact_date}'.format(contact_date=row.contact_date),
					"attachments": [frappe.attach_print(row.doctype, row.name, file_name=row.name)],
					"reference_doctype": row.doctype,
					"reference_name": row.name
				}
			try:
				enqueue(method=frappe.sendmail, queue="short",
					timeout=300, now=True, is_async=True, **email_args)
			except Exception as e:
				frappe.throw(_(f"Error in send mail {str(e)}"))


@frappe.whitelist()
def make_opportunity(source_name, target_doc=None):
	def set_missing_values(source, target):
		_set_missing_values(source, target)
	target_doc = get_mapped_doc(
		"Lead",
		source_name,
		{
			"Lead": {
				"doctype": "Opportunity",
				"field_map": {
					"campaign_name": "campaign",
					"doctype": "opportunity_from",
					"name": "party_name",
					"lead_name": "contact_display",
					"company_name": "customer_name",
					"email_id": "contact_email",
					"mobile_no": "contact_mobile",
					"campaign_name":"campaign_name",
					"source":"source",
				},
			}
		},
		target_doc,
		set_missing_values,
	)

	return target_doc


@frappe.whitelist()
def make_quotation(source_name, target_doc=None):
	print("\n\n\n************** new")

	def set_missing_values(source, target):
		from erpnext.controllers.accounts_controller import get_default_taxes_and_charges

		quotation = frappe.get_doc(target)

		company_currency = frappe.get_cached_value("Company", quotation.company, "default_currency")

		if quotation.quotation_to == "Customer" and quotation.party_name:
			party_account_currency = get_party_account_currency(
				"Customer", quotation.party_name, quotation.company
			)
		else:
			party_account_currency = company_currency

		quotation.currency = party_account_currency or company_currency

		if company_currency == quotation.currency:
			exchange_rate = 1
		else:
			exchange_rate = get_exchange_rate(
				quotation.currency, company_currency, quotation.transaction_date, args="for_selling"
			)

		quotation.conversion_rate = exchange_rate

		# get default taxes
		taxes = get_default_taxes_and_charges(
			"Sales Taxes and Charges Template", company=quotation.company
		)
		if taxes.get("taxes"):
			quotation.update(taxes)

		quotation.run_method("set_missing_values")
		quotation.run_method("calculate_taxes_and_totals")
		if not source.with_items:
			quotation.opportunity = source.name

	doclist = get_mapped_doc(
		"Opportunity",
		source_name,
		{
			"Opportunity": {
				"doctype": "Quotation",
				"field_map": {
					"opportunity_from": "quotation_to",
					"name": "enq_no",
					"campaign_name":"campaign",
					# "source":"source",
				},
			},
			"Opportunity Item": {
				"doctype": "Quotation Item",
				"field_map": {
					"parent": "prevdoc_docname",
					"parenttype": "prevdoc_doctype",
					"uom": "stock_uom",
				},
				"add_if_empty": True,
			},
		},
		target_doc,
		set_missing_values,
	)

	return doclist

@frappe.whitelist()
def set_potential_status(frm_name):
	doc = frappe.get_doc('Quotation',frm_name)
	doc.db_set('status','Potential')
	return True

@frappe.whitelist()
def make_purchase_invoice(source_name, target_doc=None):
	return get_mapped_purchase_invoice(source_name, target_doc)


def set_missing_values(source, target):
	target.run_method("set_missing_values")
	target.run_method("calculate_taxes_and_totals")

def get_mapped_purchase_invoice(source_name, target_doc=None, ignore_permissions=False):
	def postprocess(source, target):
		target.flags.ignore_permissions = ignore_permissions
		set_missing_values(source, target)
		# Get the advance paid Journal Entries in Purchase Invoice Advance
		if target.get("allocate_advances_automatically"):
			target.set_advances()

		target.set_payment_schedule()

	def update_item(obj, target, source_parent):
		target.amount = flt(obj.amount) - flt(obj.billed_amt)
		target.base_amount = target.amount * flt(source_parent.conversion_rate)
		target.qty = (
			target.amount / flt(obj.rate) if (flt(obj.rate) and flt(obj.billed_amt)) else flt(obj.qty)
		)

		item = get_item_defaults(target.item_code, source_parent.company)
		item_group = get_item_group_defaults(target.item_code, source_parent.company)
		target.cost_center = (
			obj.cost_center
			or frappe.db.get_value("Project", obj.project, "cost_center")
			or item.get("buying_cost_center")
			or item_group.get("buying_cost_center")
		)

	fields = {
		"Purchase Order": {
			"doctype": "Purchase Invoice",
			"field_map": {
				"party_account_currency": "party_account_currency",
				"supplier_warehouse": "supplier_warehouse",
			},
			# "field_no_map": ["payment_terms_template"],
			"validation": {
				"docstatus": ["=", 1],
			},
		},
		"Purchase Order Item": {
			"doctype": "Purchase Invoice Item",
			"field_map": {
				"name": "po_detail",
				"parent": "purchase_order",
			},
			"postprocess": update_item,
			"condition": lambda doc: (doc.base_amount == 0 or abs(doc.billed_amt) < abs(doc.amount)),
		},
		"Purchase Taxes and Charges": {"doctype": "Purchase Taxes and Charges", "add_if_empty": True},
	}

	doc = get_mapped_doc(
		"Purchase Order",
		source_name,
		fields,
		target_doc,
		postprocess,
		ignore_permissions=ignore_permissions,
	)
	doc.set_onload("ignore_price_list", True)

	return doc


@frappe.whitelist()
def ifi_make_sales_invoice(source_name, target_doc=None, ignore_permissions=False):
	# frappe.throw("ifi")
	def postprocess(source, target):
		set_missing_values(source, target)
		# Get the advance paid Journal Entries in Sales Invoice Advance
		if target.get("allocate_advances_automatically"):
			target.set_advances()

	def set_missing_values(source, target):
		target.flags.ignore_permissions = True
		target.run_method("set_missing_values")
		target.run_method("set_po_nos")
		target.run_method("calculate_taxes_and_totals")

		if source.company_address:
			target.update({"company_address": source.company_address})
		else:
			# set company address
			target.update(get_company_address(target.company))

		if target.company_address:
			target.update(get_fetch_values("Sales Invoice", "company_address", target.company_address))

		# set the redeem loyalty points if provided via shopping cart
		if source.loyalty_points and source.order_type == "Shopping Cart":
			target.redeem_loyalty_points = 1

		target.debit_to = get_party_account("Customer", source.customer, source.company)

	def update_item(source, target, source_parent):
		target.amount = flt(source.amount) - flt(source.billed_amt)
		target.base_amount = target.amount * flt(source_parent.conversion_rate)
		target.qty = (
			target.amount / flt(source.rate)
			if (source.rate and source.billed_amt)
			else source.qty - source.returned_qty
		)

		if source_parent.project:
			target.cost_center = frappe.db.get_value("Project", source_parent.project, "cost_center")
		if target.item_code:
			item = get_item_defaults(target.item_code, source_parent.company)
			item_group = get_item_group_defaults(target.item_code, source_parent.company)
			cost_center = item.get("selling_cost_center") or item_group.get("selling_cost_center")

			if cost_center:
				target.cost_center = cost_center

	doclist = get_mapped_doc(
		"Sales Order",
		source_name,
		{
			"Sales Order": {
				"doctype": "Sales Invoice",
				"field_map": {
					"party_account_currency": "party_account_currency",
					"payment_terms_template": "payment_terms_template",
				},
				"field_no_map": ["payment_terms_template"],
				"validation": {"docstatus": ["=", 1]},
			},
			"Sales Order Item": {
				"doctype": "Sales Invoice Item",
				"field_map": {
					"name": "so_detail",
					"parent": "sales_order",
				},
				"postprocess": update_item,
				"condition": lambda doc: doc.qty
				and (doc.base_amount == 0 or abs(doc.billed_amt) < abs(doc.amount)),
			},
			"Sales Taxes and Charges": {"doctype": "Sales Taxes and Charges",},
			"Sales Team": {"doctype": "Sales Team", "add_if_empty": True},
		},
		target_doc,
		postprocess,
		ignore_permissions=ignore_permissions,
	)

	automatically_fetch_payment_terms = cint(
		frappe.db.get_single_value("Accounts Settings", "automatically_fetch_payment_terms")
	)
	if automatically_fetch_payment_terms:
		doclist.set_payment_schedule()

	doclist.set_onload("ignore_price_list", True)

	return doclist
