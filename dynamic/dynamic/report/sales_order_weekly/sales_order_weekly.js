// Copyright (c) 2023, Dynamic and contributors
// For license information, please see license.txt
/* eslint-disable */

// Copyright (c) 2023, Dynamic and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sales Order Weekly"] = {
	"filters": [
		{
			fieldname: "range",
			label: __("Range"),
			fieldtype: "Data",

			default: "Weekly",
			reqd: 1,
			hidden:1,
		},
		{
			fieldname: "tree_type",
			label: __("Tree Type"),
			fieldtype: "Select",
			options: ["Customer Group", "Customer", "Item Group", "Item", "Territory", "Order Type", "Project","Warehouse"],
			default: "Customer",
			reqd: 1,
			hidden:1,
			read_only:1
		},
		// {
		// 	fieldname: "doc_type",
		// 	label: __("based_on"),
		// 	fieldtype: "Select",
		// 	options: ["Sales Order","Delivery Note","Sales Invoice"],
		// 	default: "Sales Invoice",
		// 	reqd: 1
		// },
		{
			fieldname: "value_quantity",
			label: __("Value Or Qty"),
			fieldtype: "Select",
			options: [
				{ "value": "Value", "label": __("Value") },
				{ "value": "Quantity", "label": __("Quantity") },
			],
			default: "Value",
			reqd: 1,
			hidden:1
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default:frappe.datetime.add_months(frappe.datetime.get_today(), 0),// frappe.defaults.get_user_default("year_start_date"),
			reqd: 1
		},
		{
			fieldname:"to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), 1),
			reqd: 1
		},
		// {
		// 	label: __("Sales Order"),
		// 	fieldname:"sales_order",
		// 	fieldtype: "Link",
		// 	options: "Sales Order",
		// 	"get_query": function() {
		// 		return {
		// 			filters: {"docstatus": ["!=", ["2"]]}
		// 		}
		// 	},
		// },
		// {
		// 	label: __("Orderd"),
		// 	fieldname:"orderd",
		// 	fieldtype: "Select",
		// 	options: [
		// 		"",
		// 		"Yes",
		// 		"No"
		// 	  ],
		// 	// options: [
		// 	// 	{ "value": "Yes", "label": __("Yes") },
		// 	// 	{ "value": "No", "label": __("No") },
		// 	// ],
		// 	default: " ",
		// },
		
		// {
		// 	fieldname: "company",
		// 	label: __("Company"),
		// 	fieldtype: "Link",
		// 	options: "Company",
		// 	default: frappe.defaults.get_user_default("Company"),
		// 	reqd: 1
		// },

	]
};
