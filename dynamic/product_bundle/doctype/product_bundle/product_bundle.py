from __future__ import unicode_literals
from distutils.ccompiler import get_default_compiler
from unittest import result
from erpnext.stock.get_item_details import get_item_defaults, get_item_group_defaults, get_brand_defaults
import frappe
from frappe import _
from frappe.defaults import get_user_default
from frappe.utils import get_link_to_form
from frappe.model.document import Document

from erpnext import get_default_company

class ProductBundle(Document):
    def autoname(self):
        self.name = self.new_item_code

    def validate(self):
        self.validate_main_item()
        # self.validate_child_items()
        from erpnext.utilities.transaction_base import validate_uom_is_integer
        validate_uom_is_integer(self, "uom", "qty")

    def on_trash(self):
        linked_doctypes = ["Delivery Note", "Sales Invoice", "POS Invoice", "Purchase Receipt", "Purchase Invoice",
            "Stock Entry", "Stock Reconciliation", "Sales Order", "Purchase Order", "Material Request"]

        invoice_links = []
        for doctype in linked_doctypes:
            item_doctype = doctype + " Item"

            if doctype == "Stock Entry":
                item_doctype = doctype + " Detail"

            invoices = frappe.db.get_all(item_doctype, {"item_code": self.new_item_code, "docstatus": 1}, ["parent"])

            for invoice in invoices:
                invoice_links.append(get_link_to_form(doctype, invoice['parent']))

        if len(invoice_links):
            frappe.throw(
                "This Product Bundle is linked with {0}. You will have to cancel these documents in order to delete this Product Bundle"
                .format(", ".join(invoice_links)), title=_("Not Allowed"))

    def validate_main_item(self):
        """Validates, main Item is not a stock item"""
        if frappe.db.get_value("Item", self.new_item_code, "is_stock_item"):
            frappe.throw(_("Parent Item {0} must not be a Stock Item").format(self.new_item_code))

    def validate_child_items(self):
        for item in self.items:
            if frappe.db.exists("Product Bundle", item.item_code):
                frappe.throw(_("Row #{0}: Child Item should not be a Product Bundle. Please remove Item {1} and Save").format(item.idx, frappe.bold(item.item_code)))


@frappe.whitelist()
def get_item_valuation_rate(item_code, company=None, warehouse=None):
    company = company or get_user_default('company')
    item = get_item_defaults(item_code, company)
    item_group = get_item_group_defaults(item_code, company)
    brand = get_brand_defaults(item_code, company)
    item_cost = 0
    # item = frappe.get_doc("Item", item_code)
    if item.get("is_stock_item"):
        if not warehouse:
            warehouse = item.get("default_warehouse") 
        if warehouse :
            item_cost = frappe.db.get_value("Bin", {
                "item_code": item_code,
                "warehouse": warehouse
            }, ["valuation_rate"]) or 0
        else:
            sql = f"""
            select AVG(valuation_rate) as valuation_rate from tabBin
            where item_code = '{item_code}'
            """ 
            valuation_rate = frappe.db.sql(sql)

            # valuation_rate = frappe.db.sql(
            #     """select sum(base_net_amount) / sum(qty*conversion_factor)
            #     from `tabPurchase Invoice Item`
            #     where item_code = %s and docstatus=1""", item_code)
            if valuation_rate:
                item_cost = valuation_rate[0][0] or 0.0

    elif frappe.db.exists("Product Bundle", item_code):
        item_cost = get_product_bundle_cost(item_code) or 0
        # frappe.msgprint(str(item_cost))

    
    return {"valuation_rate": item_cost}


@frappe.whitelist()
def get_product_bundle_cost(bundle_name):
    bundle = frappe.get_doc("Product Bundle", bundle_name)
    bundle.total_cost = 0
    for item in getattr(bundle, 'items', []):
        result = get_item_valuation_rate(item.item_code)
        item.cost = 0 if not (result and result.get("valuation_rate")) else (
            result.get("valuation_rate") or 0)
        item.qty = item.qty or 0
        item.total_cost = item.cost * item.qty
        bundle.total_cost += item.total_cost
    bundle.save()
    return bundle.total_cost


def get_default_warehouse(company):
    return frappe.db.get_single_value('Stock Settings', 'default_warehouse') or \
        frappe.db.get_value('Warehouse',
     {'warehouse_name': _('Stores'), 'company': company})
