

from erpnext import get_default_company
import frappe
from frappe import _


def validate_delivery_notes_sal_ord(doc):

    # validate sales invocie linked with sales order 
    for line in doc.items :
        if not line.against_sales_order : 
            frappe.throw(_(f"""You can not add Delivery Note without Sales Order 
                                Please Check item {line.item_name}"""))
        if  not line.sales_order_approval : 
            frappe.throw(_(f"""You can not add Delivery Note without Sales Order Approver
                                Please Check item {line.item_name}"""))

    #check reservation 
    # for line in doc.items :
    #     reservation_name = frappe.db.get_value("Sales Order Item",line.so_detail,"reservation")
    #     frappe.db.set_value('Reservation',reservation_name,{
    #         'status': 'Closed',
    #     })
  
        