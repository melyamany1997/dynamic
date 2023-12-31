# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

# For license information, please see license.txt


import json

try :
	from erpnext.stock.doctype.packed_item.packed_item import is_product_bundle
except :
	from dynamic.gebco.doctype.sales_invocie.utils import is_product_bundle
import frappe
from frappe.model.document import Document
from frappe.utils import cstr, flt

from erpnext.stock.get_item_details import get_item_details

from dynamic.gebco.doctype.sales_invocie.utils import get_product_bundle_items
class PackedItem(Document):
	pass

# def get_product_bundle_items(item_code):
# 	return frappe.db.sql("""select t1.item_code, t1.qty, t1.uom, t1.description
# 		from `tabProduct Bundle Item` t1, `tabProduct Bundle` t2
# 		where t2.new_item_code=%s and t1.parent = t2.name order by t1.idx""", item_code, as_dict=1)

# def get_packing_item_details(item, company):
# 	return frappe.db.sql("""
# 		select i.item_name, i.is_stock_item, i.description, i.stock_uom, id.default_warehouse
# 		from `tabItem` i LEFT JOIN `tabItem Default` id ON id.parent=i.name and id.company=%s
# 		where i.name = %s""",
# 		(company, item), as_dict = 1)[0]


# update function get_packing_item_details
def get_packed_item_details(item_code, company):
	item = frappe.qb.DocType("Item")
	item_default = frappe.qb.DocType("Item Default")
	query = (
		frappe.qb.from_(item)
		.left_join(item_default)
		.on((item_default.parent == item.name) & (item_default.company == company))
		.select(
			item.item_name,
			item.is_stock_item,
			item.description,
			item.stock_uom,
			item.valuation_rate,
			item_default.default_warehouse,
		)
		.where(item.name == item_code)
	)
	return query.run(as_dict=True)[0]


def get_bin_qty(item, warehouse):
	# det = frappe.db.sql("""select actual_qty, projected_qty from `tabBin`
	# 	where item_code = %s and warehouse = %s""", (item, warehouse), as_dict = 1)
	# return det and det[0] or frappe._dict()
	#updated to 
	bin_data = frappe.db.get_values(
		"Bin",
		fieldname=["actual_qty", "projected_qty"],
		filters={"item_code": item, "warehouse": warehouse},
		as_dict=True,
	)

	return bin_data[0] if bin_data else {}

def update_packing_list_item(doc, packing_item_code, qty, main_item_row, description):
	if doc.amended_from:
		old_packed_items_map = get_old_packed_item_details(doc.packed_items)
	else:
		old_packed_items_map = False
	item = get_packed_item_details(packing_item_code, doc.company)

	# check if exists
	exists = 0
	for d in doc.get("packed_items"):
		if d.parent_item == main_item_row.item_code and d.item_code == packing_item_code:
			if d.parent_detail_docname != main_item_row.name:
				d.parent_detail_docname = main_item_row.name

			pi, exists = d, 1
			break

	if not exists:
		pi = doc.append('packed_items', {})
	pi.qty = pi.qty or 0
	pi.parent_item = main_item_row.item_code
	pi.item_code = packing_item_code
	pi.item_name = item.item_name
	pi.parent_detail_docname = main_item_row.name
	pi.uom = item.stock_uom
	pi.qty += flt(qty)
	pi.conversion_factor = main_item_row.conversion_factor
	if description and not pi.description:
		pi.description = description
	if not pi.warehouse and not doc.amended_from:
		pi.warehouse = (main_item_row.warehouse if ((doc.get('is_pos') or item.is_stock_item \
			or not item.default_warehouse) and main_item_row.warehouse) else item.default_warehouse)
	if not pi.batch_no and not doc.amended_from:
		pi.batch_no = cstr(main_item_row.get("batch_no"))
	if not pi.target_warehouse:
		pi.target_warehouse = main_item_row.get("target_warehouse")
	bin = get_bin_qty(packing_item_code, pi.warehouse)
	pi.actual_qty = flt(bin.get("actual_qty"))
	pi.projected_qty = flt(bin.get("projected_qty"))
	if old_packed_items_map and old_packed_items_map.get((packing_item_code, main_item_row.item_code)):
		pi.batch_no = old_packed_items_map.get((packing_item_code, main_item_row.item_code))[0].batch_no
		pi.serial_no = old_packed_items_map.get((packing_item_code, main_item_row.item_code))[0].serial_no
		pi.warehouse = old_packed_items_map.get((packing_item_code, main_item_row.item_code))[0].warehouse

def make_packing_list(doc,fun=''):
	# cleanup_packing_list(doc)
	doc.set('packed_items', [])
	"""make packing list for Product Bundle item"""
	if doc.get("_action") and doc._action == "update_after_submit": return

	parent_items = []
	for d in doc.get("items"):
		if is_product_bundle(d.item_code):
			for i in get_product_bundle_items(d.item_code):
				if is_product_bundle(i.item_code):
					for j in get_product_bundle_items(i.item_code):
						update_packing_list_item(doc, j.item_code, flt(j.qty)*flt(i.qty)*flt(d.stock_qty), d, j.description)
					parent_items.append([i.item_code, d.name])
				else :
					update_packing_list_item(doc, i.item_code, flt(i.qty)*flt(d.stock_qty), d, i.description)

			if [d.item_code, d.name] not in parent_items:
				parent_items.append([d.item_code, d.name])

	cleanup_packing_list(doc, parent_items)

	if frappe.db.get_single_value("Selling Settings", "editable_bundle_item_rates"):
		update_product_bundle_price(doc, parent_items)

def cleanup_packing_list(doc, parent_items):
	"""Remove all those child items which are no longer present in main item table"""
	delete_list = []
	for d in doc.get("packed_items"):
		if [d.parent_item, d.parent_detail_docname] not in parent_items:
			# mark for deletion from doclist
			delete_list.append(d)

	if not delete_list:
		return doc

	packed_items = doc.get("packed_items")
	doc.set("packed_items", [])

	for d in packed_items:
		if d not in delete_list:
			add_item_to_packing_list(doc, d)

def add_item_to_packing_list(doc, packed_item):
	doc.append("packed_items", {
		'parent_item': packed_item.parent_item,
		'item_code': packed_item.item_code,
		'item_name': packed_item.item_name,
		'uom': packed_item.uom,
		'qty': packed_item.qty,
		'rate': packed_item.rate,
		'conversion_factor': packed_item.conversion_factor,
		'description': packed_item.description,
		'warehouse': packed_item.warehouse,
		'batch_no': packed_item.batch_no,
		'actual_batch_qty': packed_item.actual_batch_qty,
		'serial_no': packed_item.serial_no,
		'target_warehouse': packed_item.target_warehouse,
		'actual_qty': packed_item.actual_qty,
		'projected_qty': packed_item.projected_qty,
		'incoming_rate': packed_item.incoming_rate,
		'prevdoc_doctype': packed_item.prevdoc_doctype,
		'parent_detail_docname': packed_item.parent_detail_docname
	})

def update_product_bundle_price(doc, parent_items):
	"""Updates the prices of Product Bundles based on the rates of the Items in the bundle."""

	if not doc.get('items'):
		return

	parent_items_index = 0
	bundle_price = 0

	for bundle_item in doc.get("packed_items"):
		if parent_items[parent_items_index][0] == bundle_item.parent_item:
			bundle_item_rate = bundle_item.rate if bundle_item.rate else 0
			bundle_price += bundle_item.qty * bundle_item_rate
		else:
			update_parent_item_price(doc, parent_items[parent_items_index][0], bundle_price)

			bundle_item_rate = bundle_item.rate if bundle_item.rate else 0
			bundle_price = bundle_item.qty * bundle_item_rate
			parent_items_index += 1

	# for the last product bundle
	if doc.get("packed_items"):
		update_parent_item_price(doc, parent_items[parent_items_index][0], bundle_price)

def update_parent_item_price(doc, parent_item_code, bundle_price):
	parent_item_doc = doc.get('items', {'item_code': parent_item_code})[0]

	current_parent_item_price = parent_item_doc.amount
	if current_parent_item_price != bundle_price:
		parent_item_doc.amount = bundle_price
		update_parent_item_rate(parent_item_doc, bundle_price)

def update_parent_item_rate(parent_item_doc, bundle_price):
	parent_item_doc.rate = bundle_price/parent_item_doc.qty

@frappe.whitelist()
def get_items_from_product_bundle(args):
	args = json.loads(args)
	items = []
	bundled_items = get_product_bundle_items(args["item_code"])
	for item in bundled_items:
		args.update({
			"item_code": item.item_code,
			"qty": flt(args["quantity"]) * flt(item.qty)
		})
		items.append(get_item_details(args))

	return items

def on_doctype_update():
	frappe.db.add_index("Packed Item", ["item_code", "warehouse"])

def get_old_packed_item_details(old_packed_items):
	old_packed_items_map = {}
	for items in old_packed_items:
		old_packed_items_map.setdefault((items.item_code ,items.parent_item), []).append(items.as_dict())
	return old_packed_items_map



##### Update caculation for bundel of bundel 
#### in level one we set bundel level 2 in compicated bundel table
#### after adding level 2 
### update invocie items with level 2 items 