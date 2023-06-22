import frappe
from frappe import _


def create_item_serial_doc(doc,*args,**kwargs):
    try:
        print("doc ====================> ",doc,doc.name)
        new_doc = frappe.new_doc("item code serial")
        new_doc.item = doc.name 
        new_doc.item_group = doc.item_group 
        new_doc.save(ignore_permissions=True)
    except:
        pass