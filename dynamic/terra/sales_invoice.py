from erpnext import get_default_company
import frappe
from frappe import _

def check_return_account(doc):
    if doc.is_return:
        company = frappe.get_doc("Company",get_default_company())
        if company.get("sales_return_account"):
            default_sales_account = company.get("default_income_account")
            for item in doc.items:
                item.income_account =company.get("sales_return_account")
                


def validate_sales_invoices(doc):

    # validate sales invocie linked with sales order 
    for line in doc.items  :
        if not line.sales_order and doc.is_return ==0  : 
            frappe.throw(_(f"""You can not add Sales Invocie withou Sales Order 
                                Please Check item {line.item_name}"""))

        #check reservation 
    if doc.update_stock ==1   and not doc.is_return :
        for line in doc.items :
            reservation_name = frappe.db.get_value("Sales Order Item",line.so_detail,"reservation")
            frappe.db.set_value('Reservation',reservation_name,{
                'status': 'Closed',
            })
            # sales_order = frappe.get_doc('Sales Order Item',line.so_detail)
            # reservation_doc = frappe.get_doc('Reservation',reservation_name)
            #close Item Reservation 
            # for row in sales_order.items:
            #     frappe.db.set_value('Reservation',row.reservation,{
            #     'status': 'Closed',
            # })
        