# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


from erpnext.accounts.party import get_party_account
from erpnext.controllers.accounts_controller import get_advance_journal_entries, get_advance_payment_entries
import frappe
from frappe import _
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt, getdate, nowdate

from erpnext.controllers.selling_controller import SellingController
from frappe.utils.data import fmt_money

form_grid_templates = {"items": "templates/form_grid/item_grid.html"}


class Quotation(SellingController):
	def set_indicator(self):
		if self.docstatus == 1:
			self.indicator_color = "blue"
			self.indicator_title = "Submitted"
		if self.valid_till and getdate(self.valid_till) < getdate(nowdate()):
			self.indicator_color = "gray"
			self.indicator_title = "Expired"

	def validate(self):
		super(Quotation, self).validate()
		self.set_status()
		self.validate_uom_is_integer("stock_uom", "qty")
		self.validate_valid_till()
		self.validate_shopping_cart_items()
		self.set_customer_name()
		if self.items:
			self.with_items = 1

		from erpnext.stock.doctype.packed_item.packed_item import make_packing_list

		make_packing_list(self)


		# New functions
		self.is_return = 0
		self.clear_unallocated_advances("Sales Invoice Advance", "advances")
		self.calculate_total_advance()
	

	def validate_valid_till(self):
		if self.valid_till and getdate(self.valid_till) < getdate(self.transaction_date):
			frappe.throw(_("Valid till date cannot be before transaction date"))

	def validate_shopping_cart_items(self):
		if self.order_type != "Shopping Cart":
			return

		for item in self.items:
			has_web_item = frappe.db.exists("Website Item", {"item_code": item.item_code})

			# If variant is unpublished but template is published: valid
			template = frappe.get_cached_value("Item", item.item_code, "variant_of")
			if template and not has_web_item:
				has_web_item = frappe.db.exists("Website Item", {"item_code": template})

			if not has_web_item:
				frappe.throw(
					_("Row #{0}: Item {1} must have a Website Item for Shopping Cart Quotations").format(
						item.idx, frappe.bold(item.item_code)
					),
					title=_("Unpublished Item"),
				)

	def get_ordered_status(self):
		ordered_items = frappe._dict(
			frappe.db.get_all(
				"Sales Order Item",
				{"prevdoc_docname": self.name, "docstatus": 1},
				["item_code", "sum(qty)"],
				group_by="item_code",
				as_list=1,
			)
		)

		status = "Open"
		if ordered_items:
			status = "Ordered"

			for item in self.get("items"):
				if item.qty > ordered_items.get(item.item_code, 0.0):
					status = "Partially Ordered"

		return status

	def is_fully_ordered(self):
		return self.get_ordered_status() == "Ordered"

	def is_partially_ordered(self):
		return self.get_ordered_status() == "Partially Ordered"

	def update_lead(self):
		if self.quotation_to == "Lead" and self.party_name:
			frappe.get_doc("Lead", self.party_name).set_status(update=True)

	def set_customer_name(self):
		if self.party_name and self.quotation_to == "Customer":
			self.customer_name = frappe.db.get_value("Customer", self.party_name, "customer_name")
		elif self.party_name and self.quotation_to == "Lead":
			lead_name, company_name = frappe.db.get_value(
				"Lead", self.party_name, ["lead_name", "company_name"]
			)
			self.customer_name = company_name or lead_name

	def update_opportunity(self, status):
		for opportunity in set(d.prevdoc_docname for d in self.get("items")):
			if opportunity:
				self.update_opportunity_status(status, opportunity)

		if self.opportunity:
			self.update_opportunity_status(status)

	def update_opportunity_status(self, status, opportunity=None):
		if not opportunity:
			opportunity = self.opportunity

		opp = frappe.get_doc("Opportunity", opportunity)
		opp.set_status(status=status, update=True)

	@frappe.whitelist()
	def declare_enquiry_lost(self, lost_reasons_list, detailed_reason=None):
		if not (self.is_fully_ordered() or self.is_partially_ordered()):
			get_lost_reasons = frappe.get_list("Quotation Lost Reason", fields=["name"])
			lost_reasons_lst = [reason.get("name") for reason in get_lost_reasons]
			frappe.db.set(self, "status", "Lost")

			if detailed_reason:
				frappe.db.set(self, "order_lost_reason", detailed_reason)

			for reason in lost_reasons_list:
				if reason.get("lost_reason") in lost_reasons_lst:
					self.append("lost_reasons", reason)
				else:
					frappe.throw(
						_("Invalid lost reason {0}, please create a new lost reason").format(
							frappe.bold(reason.get("lost_reason"))
						)
					)

			self.update_opportunity("Lost")
			self.update_lead()
			self.save()

		else:
			frappe.throw(_("Cannot set as Lost as Sales Order is made."))

	def on_submit(self):
		# Check for Approving Authority
		frappe.get_doc("Authorization Control").validate_approving_authority(
			self.doctype, self.company, self.base_grand_total, self
		)

		# update enquiry status
		self.update_opportunity("Quotation")
		self.update_lead()
		self.update_against_document_in_jv()

	def on_cancel(self):
		if self.lost_reasons:
			self.lost_reasons = []
		super(Quotation, self).on_cancel()

		# update enquiry status
		self.set_status(update=True)
		self.update_opportunity("Open")
		self.update_lead()

		# unlink payment entries on cancel quotation
		from erpnext.accounts.utils import unlink_ref_doc_from_payment_entries
		unlink_ref_doc_from_payment_entries(self)

	def print_other_charges(self, docname):
		print_lst = []
		for d in self.get("taxes"):
			lst1 = []
			lst1.append(d.description)
			lst1.append(d.total)
			print_lst.append(lst1)
		return print_lst

	def on_recurring(self, reference_doc, auto_repeat_doc):
		self.valid_till = None



	# new Quotaion Payment function
	def set_total_advance_paid(self):

		
		dr_or_cr = "credit_in_account_currency"
		rev_dr_or_cr = "debit_in_account_currency"
		party = self.party_name



		if self.quotation_to == "Lead" :
			party_type = "Customer"
			party = frappe.db.get_value("Customer" , {"lead_name":self.party_name},'name')
			
		
		advance = frappe.db.sql(
			"""
			select
				account_currency, sum({dr_or_cr}) - sum({rev_dr_cr}) as amount
			from
				`tabGL Entry`
			where
				against_voucher_type = %s and against_voucher = %s and party=%s
				and docstatus = 1
		""".format(
				dr_or_cr=dr_or_cr, rev_dr_cr=rev_dr_or_cr
			),
			(self.doctype, self.name, party),
			as_dict=1,
		)  # nosec
		if advance:
			advance = advance[0]

			advance_paid = flt(advance.amount, self.precision("advance_paid"))
			formatted_advance_paid = fmt_money(
				advance_paid, precision=self.precision("advance_paid"), currency=advance.account_currency
			)

			frappe.db.set_value(self.doctype, self.name, "party_account_currency", advance.account_currency)

			if advance.account_currency == self.currency:
				order_total = self.get("rounded_total") or self.grand_total
				precision = "rounded_total" if self.get("rounded_total") else "grand_total"
			else:
				order_total = self.get("base_rounded_total") or self.base_grand_total
				precision = "base_rounded_total" if self.get("base_rounded_total") else "base_grand_total"

			formatted_order_total = fmt_money(
				order_total, precision=self.precision(precision), currency=advance.account_currency
			)

			if self.currency == self.company_currency and advance_paid > order_total:
				frappe.throw(
					_(
						"Total advance ({0}) against Quotation {1} cannot be greater than the Grand Total ({2})"
					).format(formatted_advance_paid, self.name, formatted_order_total)
				)

			frappe.db.set_value(self.doctype, self.name, "advance_paid", advance_paid)

	def get_advance_entries(self, include_unallocated=True):
		
		party_type = self.quotation_to
		party = self.party_name

		if self.quotation_to == "Lead" :
			party_type = "Customer"
			party = frappe.db.get_value("Customer" , {"lead_name":self.party_name},'name')
		
		party_account = get_party_account(party_type, party=party, company=self.company)
		amount_field = "credit_in_account_currency"
		order_field = None
		order_doctype = None

		order_list = []

		journal_entries = get_advance_journal_entries(
			party_type, party, party_account, amount_field, order_doctype, order_list, include_unallocated
		)

		payment_entries = get_advance_payment_entries(
			party_type, party, party_account, order_doctype, order_list, include_unallocated
		)

		res = journal_entries + payment_entries

		return res
	

	def update_against_document_in_jv(self):
		party_type = self.quotation_to
		party = self.party_name
		party_account = get_party_account(party_type, party=party, company=self.company)
		dr_or_cr = "credit_in_account_currency"
		lst = []
		for d in self.get("advances"):
			if flt(d.allocated_amount) > 0:
				args = frappe._dict(
					{
						"voucher_type": d.reference_type,
						"voucher_no": d.reference_name,
						"voucher_detail_no": d.reference_row,
						"against_voucher_type": self.doctype,
						"against_voucher": self.name,
						"account": party_account,
						"party_type": party_type,
						"party": party,
						"is_advance": "Yes",
						"dr_or_cr": dr_or_cr,
						"unadjusted_amount": flt(d.advance_amount),
						"allocated_amount": flt(d.allocated_amount),
						"precision": d.precision("advance_amount"),
						"exchange_rate": (
							self.conversion_rate if self.party_account_currency != self.company_currency else 1
						),
						"grand_total": (
							self.base_grand_total
							if self.party_account_currency == self.company_currency
							else self.grand_total
						),
						"outstanding_amount": self.outstanding_amount,
						"difference_account": frappe.db.get_value(
							"Company", self.company, "exchange_gain_loss_account"
						),
						"exchange_gain_loss": flt(d.get("exchange_gain_loss")),
					}
				)
				lst.append(args)

		if lst:
			# from erpnext.accounts.utils import reconcile_against_document
			from dynamic.terra.utils import reconcile_against_document
			reconcile_against_document(lst)

	def calculate_total_advance(self):
		if self.docstatus < 2:
			total_allocated_amount = sum(
				flt(adv.allocated_amount, adv.precision("allocated_amount"))
				for adv in self.get("advances")
			)			
			self.total_advance = flt(total_allocated_amount, self.precision("total_advance"))
			grand_total = self.rounded_total or self.grand_total

			if self.party_account_currency == self.currency:
				invoice_total = flt(
					grand_total - flt(self.write_off_amount), self.precision("grand_total")
				)
			else:
				base_write_off_amount = flt(
					flt(self.write_off_amount) * self.conversion_rate,
					self.precision("base_write_off_amount"),
				)
				invoice_total = (
					flt(grand_total * self.conversion_rate, self.precision("grand_total"))
					- base_write_off_amount
				)

			if invoice_total > 0 and self.total_advance > invoice_total:
				frappe.throw(
					_("Advance amount cannot be greater than {0} {1}").format(
						self.party_account_currency, invoice_total
					)
				)

			if self.docstatus == 0:
				if self.get("write_off_outstanding_amount_automatically"):
					self.write_off_amount = 0


def get_list_context(context=None):
	from erpnext.controllers.website_list_for_contact import get_list_context

	list_context = get_list_context(context)
	list_context.update(
		{
			"show_sidebar": True,
			"show_search": True,
			"no_breadcrumbs": True,
			"title": _("Quotations"),
		}
	)

	return list_context


@frappe.whitelist()
def make_sales_order(source_name, target_doc=None):
	quotation = frappe.db.get_value(
		"Quotation", source_name, ["transaction_date", "valid_till"], as_dict=1
	)
	if quotation.valid_till and (
		quotation.valid_till < quotation.transaction_date or quotation.valid_till < getdate(nowdate())
	):
		frappe.throw(_("Validity period of this quotation has ended."))
	return _make_sales_order(source_name, target_doc)


def _make_sales_order(source_name, target_doc=None, ignore_permissions=False):
	customer = _make_customer(source_name, ignore_permissions)
	ordered_items = frappe._dict(
		frappe.db.get_all(
			"Sales Order Item",
			{"prevdoc_docname": source_name, "docstatus": 1},
			["item_code", "sum(qty)"],
			group_by="item_code",
			as_list=1,
		)
	)

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
		if source.allocate_advances_automatically :
			target.run_method("set_advances")
		# if source.source:
		# 	target.source = source.source
		target.run_method("calculate_taxes_and_totals")

	def update_item(obj, target, source_parent):
		balance_qty = obj.qty - ordered_items.get(obj.item_code, 0.0)
		target.qty = balance_qty if balance_qty > 0 else 0
		target.stock_qty = flt(target.qty) * flt(obj.conversion_factor)

		if obj.against_blanket_order:
			target.against_blanket_order = obj.against_blanket_order
			target.blanket_order = obj.blanket_order
			target.blanket_order_rate = obj.blanket_order_rate

	doclist = get_mapped_doc(
		"Quotation",
		source_name,
		{
			"Quotation": {"doctype": "Sales Order", "validation": {"docstatus": ["=", 1]},
			"field_map": {
				"allocate_advances_automatically": "allocate_advances_automatically"
				}
			},
			"Quotation Item": {
				"doctype": "Sales Order Item",
				"field_map": {"parent": "prevdoc_docname"},
				"postprocess": update_item,
				"condition": lambda doc: doc.qty > 0,
			},
			"Sales Taxes and Charges": {"doctype": "Sales Taxes and Charges", "add_if_empty": True},
			"Sales Team": {"doctype": "Sales Team", "add_if_empty": True},
			"Payment Schedule": {"doctype": "Payment Schedule", "add_if_empty": True},
		},
		target_doc,
		set_missing_values,
		ignore_permissions=ignore_permissions,
	)

	# postprocess: fetch shipping address, set missing values
	doclist.set_onload("ignore_price_list", True)

	return doclist


def set_expired_status():
	# filter out submitted non expired quotations whose validity has been ended
	cond = "qo.docstatus = 1 and qo.status != 'Expired' and qo.valid_till < %s"
	# check if those QUO have SO against it
	so_against_quo = """
		SELECT
			so.name FROM `tabSales Order` so, `tabSales Order Item` so_item
		WHERE
			so_item.docstatus = 1 and so.docstatus = 1
			and so_item.parent = so.name
			and so_item.prevdoc_docname = qo.name"""

	# if not exists any SO, set status as Expired
	frappe.db.sql(
		"""UPDATE `tabQuotation` qo SET qo.status = 'Expired' WHERE {cond} and not exists({so_against_quo})""".format(
			cond=cond, so_against_quo=so_against_quo
		),
		(nowdate()),
	)


@frappe.whitelist()
def make_sales_invoice(source_name, target_doc=None):
	return _make_sales_invoice(source_name, target_doc)


def _make_sales_invoice(source_name, target_doc=None, ignore_permissions=False):
	customer = _make_customer(source_name, ignore_permissions)

	def set_missing_values(source, target):
		if customer:
			target.customer = customer.name
			target.customer_name = customer.customer_name

		target.flags.ignore_permissions = ignore_permissions
		target.run_method("set_missing_values")
		target.run_method("calculate_taxes_and_totals")

	def update_item(obj, target, source_parent):
		target.cost_center = None
		target.stock_qty = flt(obj.qty) * flt(obj.conversion_factor)

	doclist = get_mapped_doc(
		"Quotation",
		source_name,
		{
			"Quotation": {"doctype": "Sales Invoice", "validation": {"docstatus": ["=", 1]}},
			"Quotation Item": {"doctype": "Sales Invoice Item", "postprocess": update_item},
			"Sales Taxes and Charges": {"doctype": "Sales Taxes and Charges", "add_if_empty": True},
			"Sales Team": {"doctype": "Sales Team", "add_if_empty": True},
		},
		target_doc,
		set_missing_values,
		ignore_permissions=ignore_permissions,
	)

	doclist.set_onload("ignore_price_list", True)

	return doclist

@frappe.whitelist()
def make_customer(source_name, ignore_permissions=False):
	return  _make_customer(source_name, ignore_permissions)


def _make_customer(source_name, ignore_permissions=False):
	quotation = frappe.db.get_value(
		"Quotation", source_name, ["order_type", "party_name", "customer_name"], as_dict=1
	)

	if quotation and quotation.get("party_name"):
		if not frappe.db.exists("Customer", quotation.get("party_name")):
			lead_name = quotation.get("party_name")
			customer_name = frappe.db.get_value(
				"Customer", {"lead_name": lead_name}, ["name", "customer_name"], as_dict=True
			)
			if not customer_name:
				from erpnext.crm.doctype.lead.lead import _make_customer

				customer_doclist = _make_customer(lead_name, ignore_permissions=ignore_permissions)
				customer = frappe.get_doc(customer_doclist)
				customer.flags.ignore_permissions = ignore_permissions
				if quotation.get("party_name") == "Shopping Cart":
					customer.customer_group = frappe.db.get_value(
						"E Commerce Settings", None, "default_customer_group"
					)

				try:
					customer.insert()
					return customer
				except frappe.NameError:
					if frappe.defaults.get_global_default("cust_master_name") == "Customer Name":
						customer.run_method("autoname")
						customer.name += "-" + lead_name
						customer.insert()
						return customer
					else:
						raise
				except frappe.MandatoryError as e:
					mandatory_fields = e.args[0].split(":")[1].split(",")
					mandatory_fields = [customer.meta.get_label(field.strip()) for field in mandatory_fields]

					frappe.local.message_log = []
					lead_link = frappe.utils.get_link_to_form("Lead", lead_name)
					message = (
						_("Could not auto create Customer due to the following missing mandatory field(s):") + "<br>"
					)
					message += "<br><ul><li>" + "</li><li>".join(mandatory_fields) + "</li></ul>"
					message += _("Please create Customer from Lead {0}.").format(lead_link)

					frappe.throw(message, title=_("Mandatory Missing"))
			else:
				return customer_name
		else:
			return frappe.get_doc("Customer", quotation.get("party_name"))


@frappe.whitelist()
def make_sales_order_lead(source_name, ignore_permissions=False):
	customer = make_customer_from_lead(source_name, ignore_permissions=False)
	new_sales_order  = frappe.new_doc("Sales Order")
	new_sales_order.customer = customer.name
	return new_sales_order
	

@frappe.whitelist()
def make_customer_from_lead(source_name, ignore_permissions=False): 
	lead = frappe.db.get_value(
		"Lead", source_name, ["lead_name"], as_dict=1
	)

	if lead and lead.get("lead_name"):
		if not frappe.db.exists("Customer", lead.get("lead_name")):
			lead_name = source_name
			customer_name = frappe.db.get_value(
				"Customer", {"customer_name": lead_name}, ["name", "customer_name"], as_dict=True
			)
			if not customer_name:
				from erpnext.crm.doctype.lead.lead import _make_customer

				customer_doclist = _make_customer(lead_name, ignore_permissions=ignore_permissions)
				customer = frappe.get_doc(customer_doclist)
				customer.flags.ignore_permissions = ignore_permissions
				if lead.get("lead_name") == "Shopping Cart":
					customer.customer_group = frappe.db.get_value(
						"E Commerce Settings", None, "default_customer_group"
					)

				try:
					customer.insert()
					return customer
				except frappe.NameError:
					if frappe.defaults.get_global_default("cust_master_name") == "Customer Name":
						customer.run_method("autoname")
						customer.name += "-" + lead_name
						customer.insert()
						return customer
					else:
						raise
				except frappe.MandatoryError as e:
					mandatory_fields = e.args[0].split(":")[1].split(",")
					mandatory_fields = [customer.meta.get_label(field.strip()) for field in mandatory_fields]

					frappe.local.message_log = []
					lead_link = frappe.utils.get_link_to_form("Lead", lead_name)
					message = (
						_("Could not auto create Customer due to the following missing mandatory field(s):") + "<br>"
					)
					message += "<br><ul><li>" + "</li><li>".join(mandatory_fields) + "</li></ul>"
					message += _("Please create Customer from Lead {0}.").format(lead_link)

					frappe.throw(message, title=_("Mandatory Missing"))
			else:
				return customer_name
		else:
			return frappe.get_doc("Customer", lead.get("lead_name"))



from collections import defaultdict
from frappe.desk.reportview import get_filters_cond, get_match_cond
from frappe.utils import nowdate, unique



def get_fields(doctype, fields=None):
	if fields is None:
		fields = []
	meta = frappe.get_meta(doctype)
	fields.extend(meta.get_search_fields())

	if meta.title_field and not meta.title_field.strip() in fields:
		fields.insert(1, meta.title_field.strip())

	return unique(fields)
@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def matrerial_request_query(doctype, txt, searchfield, start, page_len, filters, as_dict=False):
	doctype = "Material Request"
	conditions = []
	name_sql  =  frappe.db.sql("""SELECT A.name FROM `tabMaterial Request` A 
				 INNER JOIN `tabMaterial Request Item` B 
				 ON A.name = B.parent
				 WHERE A.docstatus = "1" AND A.has_quotation="1"
				 """)
	return name_sql 

	


