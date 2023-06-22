// Copyright (c) 2022, Dynamic and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Total Balance"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label":__("From Date"),
			"fieldtype":"Date",
			reqd:1,
			"default":frappe.datetime.get_today(),
		},
		{
			"fieldname":"to_date",
			"label":__("To date"),
			"fieldtype":"Date",
			"default":frappe.datetime.add_days(frappe.datetime.get_today(),1)
		},
		{
			"fieldname": "mode_of_payment",
			"label": __("Mode Of Payment"),
			"fieldtype": "Link",
			"options": "Mode of Payment",
			"default": '',
			reqd: 1
		},
	]
};
