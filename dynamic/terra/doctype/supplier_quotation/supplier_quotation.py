import frappe 
from erpnext.stock.doctype.material_request.material_request import set_missing_values

from frappe.model.mapper import get_mapped_doc
def submit_supplier_quotation(self) :
    requested = []
    for item in self.items :
        if item.material_request and item.material_request not in requested :
            requested.append(item.material_request)
    for matrial_request in requested  :
        frappe.db.sql(f""" 
        update `tabMaterial Request` set status= 'Ordered'  , quotation ='{self.name}' , has_quotation = 1 
        WHERE name ='{matrial_request}' and material_request_type = 'Price Request'  and status <> "Partially Ordered" and status <> "Ordered"
        
                """)
        frappe.db.commit()



@frappe.whitelist()
def make_supplier_quotation(source_name, target_doc=None):
	def postprocess(source, target_doc):
		set_missing_values(source, target_doc)

	doclist = get_mapped_doc(
		"Material Request",
		source_name,
		{
			"Material Request": {
				"doctype": "Supplier Quotation",
				"validation": {"docstatus": ["=", 1], "material_request_type": ["in", ["Purchase" , "Price Reques"]]},
			},
			"Material Request Item": {
				"doctype": "Supplier Quotation Item",
				"field_map": {
					"name": "material_request_item",
					"parent": "material_request",
					"sales_order": "sales_order",
				},
			},
		},
		target_doc,
		postprocess,
	)

	return doclist



@frappe.whitelist()
def make_request_for_quotation(source_name, target_doc=None):
	doclist = get_mapped_doc(
		"Material Request",
		source_name,
		{
			"Material Request": {
				"doctype": "Request for Quotation",
				"validation": {"docstatus": ["=", 1], "material_request_type": ["in", ["Purchase" , "Price Reques"]]},
			},
			"Material Request Item": {
				"doctype": "Request for Quotation Item",
				"field_map": [
					["name", "material_request_item"],
					["parent", "material_request"],
					["uom", "uom"],
				],
			},
		},
		target_doc,
	)

	return doclist