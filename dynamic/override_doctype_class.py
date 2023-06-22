import json
import frappe

from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice as ERPNextSalesInvoice
from erpnext.accounts.doctype.payment_entry.payment_entry import PaymentEntry as ERPNextPaymentEntry
from erpnext.selling.doctype.sales_order.sales_order import SalesOrder as ERPNextSalesOrder
from erpnext.selling.doctype.quotation.quotation import Quotation as ERPNextQuotation
from erpnext.payroll.doctype.salary_slip.salary_slip import SalarySlip as ERPNextSalarySlip
from erpnext.crm.doctype.lead.lead import Lead as ERPNextLead


# Default ERP Class
PaymentEntry = ERPNextPaymentEntry
SalesOrder = ERPNextSalesOrder
Quotation = ERPNextQuotation
SalarySlip = ERPNextSalarySlip
Lead = ERPNextLead
SalesInvoice = ERPNextSalesInvoice








# doctype js override
doctype_js = {
    "Sales Invoice": "public/js/sales_invoice.js",
    "Sales Order": "public/js/sales_order.js",
    "Stock Entry": "public/js/stock_entry.js",
    "Purchase Order": "public/js/purchase_order.js",
    "Purchase Invoice": "public/js/purchase_invoice.js",
    "Product Bundle": "product_bundle/doctype/product_bundle/product_bundle.js",
    "Payment Entry": "public/js/payment_entry.js",
    "Landed Cost Voucher": "public/js/landed_cost_voucher.js",
    "Delivery Note": "public/js/delivery_note.js",
    "Lead":"public/js/lead.js",
    "Supplier":"public/js/supplier.js",
    "Customer":"public/js/customer.js",
}

active_domains = frappe.get_active_domains()


# print("override doctype_js in hooks",'hooks.doctype_js')

if "Terra" in active_domains:
    # frappe.msgprint('terra')
    # override doctype clesses
    from dynamic.terra.doctype.payment_entry.payment_entry import PaymentEntry as TerraPaymentEntry
    from dynamic.terra.doctype.sales_order.sales_order import SalesOrder as TerraSalesOrder
    from dynamic.terra.doctype.quotation.quotation import Quotation as TerraQuotation

    PaymentEntry = TerraPaymentEntry

    SalesOrder = TerraSalesOrder

    Quotation = TerraQuotation




if "Dynamic HR" in active_domains :
    pass



if "Elevana" in active_domains :

    from dynamic.elevana.doctype.sales_invoice.sales_invoice import SalesInvoice as ElevanaSalesInvoice
    SalesInvoice = ElevanaSalesInvoice


if "Dynamic Payroll" in active_domains :
    from dynamic.dynamic_payroll.doctype.salary_slip.salary_slip import SalarySlip as PayrollSalarySlip

    SalarySlip = PayrollSalarySlip


if "Teba" in active_domains:
    from dynamic.terra.doctype.payment_entry.payment_entry import PaymentEntry as TerraPaymentEntry

    PaymentEntry = TerraPaymentEntry















    # override doctype js
    #doctype_js["Payment Entry"] = "terra/doctype/payment_entry/payment_entry.js"






# override doctype_js in hooks

# # try :
# from dynamic import override_doctype_js
# # # from hooks import doctype_js
# from dynamic import hooks

# # frappe.msgprint("override doctype_js in hooks")

# hooks.doctype_js = override_doctype_js.doctype_js
# frappe.msgprint(str(hooks.doctype_js))

# except Exception as e  :
    
#     print("override doctype_js in hooks error",str(e))



from dynamic import hooks
# hooks.doctype_js = doctype_js

# with open(DOCTYPE_JS_FILE_PATH, "w") as write_file:
    
#     json.dump(doctype_js, write_file, indent=4)



# frappe.msgprint (str(doctype_js.get("Payment Entry")))

# frappe.msgprint ("hooks doctype js override ==========> " , hooks.doctype_js.get("Payment Entry"))
