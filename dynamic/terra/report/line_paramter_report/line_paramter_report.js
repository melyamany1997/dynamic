// Copyright (c) 2023, Dynamic and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Line Paramter Report"] = {
	"filters": [
		// {
		// 	fieldname: "from_date",
		// 	label: __("From Date"),
		// 	fieldtype: "Date"
		// },
		// {
		// 	fieldname: "to_date",
		// 	label: __("To Date"),
		// 	fieldtype: "Date"
		// },
		{
			fieldname: "dt",
			label: __("Doctype"),
			"fieldtype": "Link",
			"options": "DocType",
			"get_query": function() {
				
				return {
					filters: {"name": ["in", ["Work Order", "Job Card"]]}
				}
			},
		},
		{
			fieldname: "dn1",
			label: __("Work Order"),
			fieldtype: "Link",
			options:"Work Order"
		},
		{
			fieldname: "dn2",
			label: __("Job Card"),
			fieldtype: "Link",
			options:"Job Card"
		},


		// {
		// 	fieldname: "dn",
		// 	label: __("Doctype Name"),
		// 	fieldtype: "Dynamic Link",
		// 	// options : "dt"
		// 	"get_options": function() {
		// 		// console.log(frappe.query_report.get_values().dn)
		// 		var  applicant_type = frappe.query_report.get_values().dn
		// 		if (!frappe.query_report.get_filter_value('dn')){
		// 			  applicant_type = frappe.query_report.get_filter_value('dt');
					
				
		// 		}
		// 		return applicant_type;
		// 	}
		// },

	]
};
