# Copyright (c) 2022, Dynamic and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.contacts.doctype.address.address import get_company_address
from frappe.model.mapper import get_mapped_doc
from frappe.model.utils import get_fetch_values
from frappe.utils import add_days, cint, cstr, flt, get_link_to_form, getdate, nowdate, strip_html
from erpnext.stock.doctype.item.item import get_item_defaults
from erpnext.setup.doctype.item_group.item_group import get_item_group_defaults
from frappe  import _
class SalesOrderApproval(Document):
	def validate(self):
		self.validate_qty_against_sales_order()
		for item in self.items:
			item.approved_qty = item.qty
			item.remaining_qty = item.qty
		self.status = "Draft"
	def before_submit(self):
		self.status ="To Deliver"
		# frappe.db.sql(f"""
		# update `tabSales Order` set status='To Deliver' where name='{item.against_sales_order}'
		# """)
		# frappe.db.commit()
		
	def on_submit(self):
		self.validate_qty_against_sales_order()
		for item in self.items:
			if item.get("against_sales_order"):
				sql = f"""
				update `tabSales Order Item` set approved_qty = approved_qty + {item.qty},
				remaining_qty = qty - approved_qty  where parent='{item.against_sales_order}' 
				and item_code = '{item.item_code}' 
				"""
				frappe.db.sql(sql)
				frappe.db.commit()
		# frappe.db.sql(f""" AND name = '{item.so_detail}'
		# update `tabSales Order` set status='To Deliver' where name='{item.against_sales_order}'
		# """)
		# frappe.db.commit()

	def validate_qty_against_sales_order(self):
		for item in self.items :
			qty =  0
			item_sales_order_qty = frappe.db.sql(f""" select approved_qty , remaining_qty , qty from `tabSales Order Item`
												 WHERE name = '{item.so_detail}' """ ,as_dict =1)
			if not item_sales_order_qty or len(item_sales_order_qty) ==0 :
				frappe.throw("Can Not Complete Proccess")
			if item_sales_order_qty[0].get("approved_qty") :
				qty = float(item_sales_order_qty[0].get("remaining_qty") ) 
			if not  item_sales_order_qty[0].get("approved_qty") :
				qty = 	item_sales_order_qty[0].get("qty") 		
			# frappe.throw(str(qty))
			if item.qty > qty :
				frappe.throw(f""" Order Qty is {item_sales_order_qty[0].get("qty")}   And approved Qty {item_sales_order_qty[0].get("approved_qty")} you can not approve {item.qty}""")
	def on_cancel(self):
		try : 
			# 1
			#self.cancel_delivery_note()
			#2
			self.reset_qtys()
		except Exception as ex :
			frappe.throw(_(str(ex)))


	def cancel_delivery_note(self):
		# get all delivery note linked with this approval
		sql = f""" select parent from `tabDelivery Note Item` where sales_order_approval = '{self.name}'"""
		res = frappe.db.sql(sql,as_dict=1)
		for r in res:
			doc = frappe.get_doc("Delivery Note",r.parent)
			doc.cancel()



	def reset_qtys(self):
		# we must cancel delivery note if exist

		# decrease so approved qty and so increase remaining qty  with cancelled approval qty 
		
		for item in self.items:
			sql = f"""
				update `tabSales Order Item` 
				set approved_qty = approved_qty - {item.qty},
				remaining_qty = remaining_qty + {item.qty}
				where parent = '{item.against_sales_order}' and item_code = '{item.item_code}'
			"""
			frappe.db.sql(sql)
			frappe.db.commit()

		

@frappe.whitelist()
def make_sales_order_approval(source_name, target_doc=None, skip_item_mapping=False):
	def set_missing_values(source, target):
		target.run_method("set_missing_values")
		target.run_method("set_po_nos")
		target.run_method("calculate_taxes_and_totals")

		if source.company_address:
			target.update({"company_address": source.company_address})
		else:
			# set company address
			target.update(get_company_address(target.company))

		if target.company_address:
			target.update(get_fetch_values("Sales Order Approval", "company_address", target.company_address))

	def update_item(source, target, source_parent):
		target.base_amount = (flt(source.qty) - flt(source.approved_qty)) * flt(source.base_rate)
		target.amount = (flt(source.qty) - flt(source.approved_qty)) * flt(source.rate)
		target.qty = flt(source.qty) - flt(source.approved_qty)

		item = get_item_defaults(target.item_code, source_parent.company)
		item_group = get_item_group_defaults(target.item_code, source_parent.company)

		if item:
			target.cost_center = (
				frappe.db.get_value("Project", source_parent.project, "cost_center")
				or item.get("buying_cost_center")
				or item_group.get("buying_cost_center")
			)

	mapper = {
		"Sales Order": {"doctype": "Sales Order Approval",
		  "field_map": {
				"delivery_date":"delivery_date"
			},"validation": {"docstatus": ["=", 1]}},
		"Sales Taxes and Charges": {"doctype": "Sales Taxes and Charges", "add_if_empty": True},
		"Sales Team": {"doctype": "Sales Team", "add_if_empty": True},
	}

	if not skip_item_mapping:

		def condition(doc):
			print("doc =============================> ",doc.qty)
			if doc.qty - doc.approved_qty == 0:
				return False
			# make_mapped_doc sets js `args` into `frappe.flags.args`
			if frappe.flags.args and frappe.flags.args.delivery_dates:
				if cstr(doc.delivery_date) not in frappe.flags.args.delivery_dates:
					return False
			return abs(doc.delivered_qty) < abs(doc.qty) and doc.delivered_by_supplier != 1

		mapper["Sales Order Item"] = {
			"doctype": "Sales Order Approval Item",
			"field_map": {
				"rate": "rate",
				"name": "so_detail",
				"parent": "against_sales_order",
				"qty":"sales_order_qty"
			},
			"postprocess": update_item,
			"condition": condition,
		}

	target_doc = get_mapped_doc("Sales Order", source_name, mapper, target_doc, set_missing_values)

	target_doc.set_onload("ignore_price_list", True)



	return target_doc



@frappe.whitelist()
def make_delivery_note(source_name, target_doc=None, skip_item_mapping=False):
	def set_missing_values(source, target):
		target.run_method("set_missing_values")
		target.run_method("set_po_nos")
		target.run_method("calculate_taxes_and_totals")

		if source.company_address:
			target.update({"company_address": source.company_address})
		else:
			# set company address
			target.update(get_company_address(target.company))

		if target.company_address:
			target.update(get_fetch_values("Delivery Note", "company_address", target.company_address))

	def update_item(source, target, source_parent):
		target.base_amount = (flt(source.qty) - flt(source.qty)) * flt(source.base_rate)
		target.amount = flt(source.qty)  * flt(source.rate)
		if source.approved_qty == source.remaining_qty:
			target.qty = source.approved_qty
		else:
			target.qty =  flt(source.remaining_qty)

		#target.qty = flt(source.qty) - flt(source.qty)

		item = get_item_defaults(target.item_code, source_parent.company)
		item_group = get_item_group_defaults(target.item_code, source_parent.company)

		if item:
			target.cost_center = (
				frappe.db.get_value("Project", source_parent.project, "cost_center")
				or item.get("buying_cost_center")
				or item_group.get("buying_cost_center")
			)

	mapper = {
		"Sales Order Approval": {"doctype": "Delivery Note", "validation": {"docstatus": ["=", 1]}},
		"Sales Taxes and Charges": {"doctype": "Sales Taxes and Charges", "add_if_empty": True},
		"Sales Team": {"doctype": "Sales Team", "add_if_empty": True},
		# "Sales Order Approval Item" :{"doctype": "Delivery Note Item", "add_if_empty": True}
	}

	# if not skip_item_mapping:

	# 	# def condition(doc):
	# 	# 	# make_mapped_doc sets js `args` into `frappe.flags.args`
	# 	# 	if frappe.flags.args and frappe.flags.args.delivery_dates:
	# 	# 		if cstr(doc.delivery_date) not in frappe.flags.args.delivery_dates:
	# 	# 			return False
	# 	# 	return abs(doc.qty) < abs(doc.qty) and doc.delivered_by_supplier != 1

	mapper["Sales Order Approval Item"] = {
		"doctype": "Delivery Note Item",
		"field_map": {
				"against_sales_order": "against_sales_order",
				"so_detail":"so_detail",
				"qty":"qty",
				"parent":"sales_order_approval"
		},
		"postprocess": update_item
	}

	target_doc = get_mapped_doc("Sales Order Approval", source_name, mapper, target_doc, set_missing_values)

	target_doc.set_onload("ignore_price_list", True)

	return target_doc














"""
on sales order  -----> deliverd ,remaining,

"""