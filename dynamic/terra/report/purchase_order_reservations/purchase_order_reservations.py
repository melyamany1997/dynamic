# Copyright (c) 2022, Dynamic and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	columns, data = [], []
	data = get_data(filters)
	columns = get_columns()
	return columns, data


def get_data(filters):
	conditions = " where 1=1 "
	if filters.get("puchase_order"):
		conditions += " and por.purchase_order='%s'"%filters.get("puchase_order")

	sql = f"""
		    select
			tpoi.item_code, 
			por.purchase_order , 
			por.reserved_qty reserved_qty ,
			sum(tpri.qty) accepted_qty,
			tpoi.qty - sum(tpri.qty) as 'remaining_qty'
			from
			`tabReservation Purchase Order` por
			inner join `tabPurchase Order Item` tpoi 
			on tpoi.parent  = por.purchase_order  and tpoi.item_code = por.item
			left join `tabPurchase Receipt Item` tpri
			on tpoi.parent = tpri.purchase_order  and tpoi.item_code  = tpri.item_code and tpri.purchase_order is not null and tpri.docstatus =1
			{conditions}
			GROUP by  por.purchase_order,tpri.purchase_order
		
	"""

	result = frappe.db.sql(sql,as_dict=1)
	return result

def get_columns():
	columns = [
		{
            "label": _("Item Code"),
            "fieldname": "item_code",
            "fieldtype": "Link",
			"options":"Item",
            "width": 150
        },
		{
            "label": _("Purchase Order"),
            "fieldname": "purchase_order",
            "fieldtype": "Link",
			"options":"Purchase Order",
            "width": 190
        },
		{
            "label": _("Reserved Qty"),
            "fieldname": "reserved_qty",
            "fieldtype": "Data",
            "width": 160
        },
		{
            "label": _("Accepted QTY"),
            "fieldname": "accepted_qty",
            "fieldtype": "Data",
            "width": 160
        },
		{
            "label": _("Remaining QTY"),
            "fieldname": "remaining_qty",
            "fieldtype": "Data",
            "width": 160
        },
	
	
		
	]
	return columns