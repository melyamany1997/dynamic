// Copyright (c) 2022, Dynamic and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sales Person Target Summary"] = {
	"filters": [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.add_days(frappe.datetime.get_today(),1),
			// reqd: 1
		},
		{
			fieldname: "territory",
			label: __("Territory"),
			fieldtype: "Link",
			options:"Territory"
		},
		{
			fieldname: "cost_center",
			label: __("Cost Center"),
			fieldtype: "Link",
			options:"Cost Center"
		},
		{
			fieldname: "sales_person",
			label: __("Sales Person"),
			fieldtype: "Link",
			options:"Sales Person"
		},
		{
			fieldname: "action",
			label: __("Action"),
			fieldtype: "Link",
			options:"Action"
		},
	]
};
