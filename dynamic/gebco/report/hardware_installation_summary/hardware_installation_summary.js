// Copyright (c) 2022, Dynamic and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Hardware Installation Summary"] = {
	"filters": [
		{
			fieldname: "from_date",
			label: __("From Time"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
		  },
		  {
			fieldname: "to_date",
			label: __("To time"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
		  },
		  {
			"fieldname":"source",
			"label": __("Source"),
			"fieldtype": "Link",
			"options": "DocType",
			// "default": "Sales Order",
			// "reqd":1,
			"get_query": function() {
				return {
					filters: {"name": ["in", ["Sales Order", "Installation Request","Installation Order"]]}
				}
			},
	  on_change: () => {
		frappe.query_report.set_filter_value("doc_name", ' ');
				frappe.query_report.refresh();
	  },
		},
	{
	  fieldname: "doc_name",
	  label: __("Document"),
	  fieldtype: "Dynamic Link",
	  "get_options": function() {
				var applicant_type = frappe.query_report.get_filter_value('source');
				var applicant = frappe.query_report.get_filter_value('doc_name');
				if(applicant && !applicant_type) {
					frappe.throw(__("Please select Party Type first"));
				}
				return applicant_type;
			}
	},
	]
};
