# Copyright (c) 2023, Dynamic and contributors
# For license information, please see license.txt

# Copyright (c) 2022, Dynamic and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	columns, data = [], []
	data = get_data(filters)
	columns = get_columns(filters)
	return columns, data


def get_data(filters):
	
	conditions = " where 1=1 "
	if filters.get("dn1") or filters.get("dn2"):
		if(filters.get("dt") == 'Work Order'):
			conditions += " and work_order = '%s'"%filters.get("dn1")
		elif(filters.get("dt") == 'Job Card'):
			conditions += " and job_card = '%s'"%filters.get("dn2")


	sql = f"""
	select *,TIME(start_time) as start_time from `tabLINE PARAMETER`
		{conditions}
	"""
	result = frappe.db.sql(sql,as_dict=1)
	return result

def get_columns(filters):
	columns = [
		{
            "label": _("Linked Data Start Time"),
            "fieldname": "start_time",
            "fieldtype": "Time",
            "width": 150
        },
		
		{
            "label": _("Acid Wash Basin Line Speed"),
            "fieldname": "awb_l",
            "fieldtype": "Data",
            "width": 150
        },
		{
            "label": _("Acid Wash Basin D-Bruches"),
            "fieldname": "awb_d",
            "fieldtype": "Data",
            "width": 150
        },
		{
            "label": _("Acid Wash Basin PH"),
            "fieldname": "awb_ph",
            "fieldtype": "Data",
            "width": 150
        },
		{
            "label": _("Acid Wash Basin C"),
            "fieldname": "awb_c",
            "fieldtype": "Data",
            "width": 150
        },
		{
            "label": _("Alkali Wash Basin PH"),
            "fieldname": "kwb_ph",
            "fieldtype": "Data",
            "width": 150
        },
		{
            "label": _("Alkali Wash Basin C"),
            "fieldname": "kwb_c",
            "fieldtype": "Data",
            "width": 150
        },
		{
            "label": _("Slat Basin PH"),
            "fieldname": "ph",
            "fieldtype": "Data",
            "width": 150
        },
		{
            "label": _("Slat Basin C"),
            "fieldname": "c",
            "fieldtype": "Data",
            "width": 150
        },
		{
            "label": _("Slat Basin TSC"),
            "fieldname": "tsc",
            "fieldtype": "Data",
            "width": 150
        },
		{
            "label": _("Slat Basin Drying Oven"),
            "fieldname": "drying_oven",
            "fieldtype": "Data",
            "width": 150
        },
		{
            "label": _("Latex Basin PH"),
            "fieldname": "lb_ph",
            "fieldtype": "Data",
            "width": 150
        },
		{
            "label": _("Latex Basin C"),
            "fieldname": "lb_c",
            "fieldtype": "Data",
            "width": 150
        },
		{
            "label": _("Latex Basin TSC"),
            "fieldname": "lb_tsc",
            "fieldtype": "Data",
            "width": 150
        },
		{
            "label": _("Latex Basin Latex Oven"),
            "fieldname": "latex_oven",
            "fieldtype": "Data",
            "width": 150
        },
		{
            "label": _("Polymer Basin PH"),
            "fieldname": "pb_ph",
            "fieldtype": "Data",
            "width": 150
        },
		{
            "label": _("Polymer Basin C"),
            "fieldname": "pb_c",
            "fieldtype": "Data",
            "width": 150
        },
		{
            "label": _("Polymer Basin TSC"),
            "fieldname": "pb_tsc",
            "fieldtype": "Data",
            "width": 150
        },
		{
            "label": _("Polymer Basin Polymer Oven"),
            "fieldname": "polymer_oven",
            "fieldtype": "Data",
            "width": 150
        },
		{
            "label": _("MAIN Brush Direction"),
            "fieldname": "brush_direction",
            "fieldtype": "Data",
            "width": 150
        },
		{
            "label": _("MAIN Main Oven F"),
            "fieldname": "main_oven_f",
            "fieldtype": "Data",
            "width": 150
        },
		{
            "label": _("MAIN Drying Oven F"),
            "fieldname": "drying_oven_f",
            "fieldtype": "Data",
            "width": 150
        },
		
		
	]
	if (filters.get("dt") == 'Work Order'):
		columns.append({
            "label": _("Work Order"),
            "fieldname": "work_order",
            "fieldtype": "Link",
			"options":"Work Order",
            "width": 150
        },)
	elif(filters.get("dt") == 'Job Card'):
		columns.append(
		{
            "label": _("Job Card"),
            "fieldname": "job_card",
            "fieldtype": "Link",
			"options":"Job Card",
            "width": 150
        })
	return columns