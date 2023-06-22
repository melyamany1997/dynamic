// Copyright (c) 2022, Dynamic and contributors
// For license information, please see license.txt
/* eslint-disable */

// frappe.query_reports["Balance Sheet Date"] = {
// 	"filters": [

// 	]
// };


frappe.require("assets/erpnext/js/financial_statements.js", function() {
	frappe.query_reports["Balance Sheet Date"] = $.extend({}, erpnext.financial_statements);

	// erpnext.utils.add_dimensions('Balance Sheet', 10);

	frappe.query_reports["Balance Sheet Date"]["filters"].push({
		"fieldname": "accumulated_values",
		"label": __("Accumulated Values"),
		"fieldtype": "Check",
		"default": 1
	});

	frappe.query_reports["Balance Sheet Date"]["filters"].push({
		"fieldname": "include_default_book_entries",
		"label": __("Include Default Book Entries"),
		"fieldtype": "Check",
		"default": 1
	});
});