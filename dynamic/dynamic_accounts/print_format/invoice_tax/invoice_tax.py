import frappe
from frappe.utils.data import get_link_to_form

@frappe.whitelist()
def get_invoice_tax_data(doc):
    doc = frappe.get_doc("Sales Invoice", doc)
    total_discount_amount = sum([(x.discount_amount or 0) for x in doc.items])
    total_tax_amount = sum([(x.tax_amount or 0) for x in doc.items])
    server_url = host_name = frappe.local.conf.host_name or frappe.local.conf.hostname
    return {
        "total_discount_amount" : total_discount_amount ,
        "total_tax_amount" : total_tax_amount ,
        "server_url" : server_url ,
    }