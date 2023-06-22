// Copyright (c) 2022, Dynamic and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sales Person Comminion"] = {
	"filters": [
		{
			"fieldname":"start_date",
			"label": ("From  Date"),
			"fieldtype": "Date",
			

		},
		{
			"fieldname":"end_date",
			"label": ("To Date"),
			"fieldtype": "Date",

		},
		{
			"fieldname":"sales_person",
			"label": ("Sales Person"),
			"fieldtype": "Link",
			"options": "Sales Person"

		},
		{
			"fieldname":"item_group",
			"label": ("Item Group"),
			"fieldtype": "Link",
			"options": "Item Group"

		},
	]
};
