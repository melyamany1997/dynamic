
from frappe import _
import frappe
from dynamic.dynamic_accounts.setup import add_properties_journal_auto
def install():
    try:
        add_properties_journal_auto()
    except Exception as e:
        frappe.throw(_(str(e)))
    pass