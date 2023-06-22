# Copyright (c) 2022, Dynamic and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Car(Document):
    pass


@frappe.whitelist()
# @frappe.validate_and_sanitize_search_inputs
def get_serial_no_query(doctype, txt, searchfield, start, page_len, filters):
    docname = filters.get("docname") or ""
    sql = f"""
	select serial_no.name,serial_no.item_code from `tabSerial No` serial_no where serial_no.name not in 
	(
		select car.serial_no from tabCar car where car.docstatus < 2
		and car.name <> '{docname}'
		 and IFNULL(car.serial_no,'') <> '' 
	) and
		( serial_no.serial_no like '%{txt}%' or  serial_no.name like '%{txt}%' or serial_no.item_code like '%{txt}%')
		limit {start} , {page_len}"""
    # frappe.msgprint(sql)
    return frappe.db.sql(sql)
