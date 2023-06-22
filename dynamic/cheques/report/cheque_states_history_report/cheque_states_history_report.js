// Copyright (c) 2022, Dynamic and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Cheque States History Report"] = {
	"filters": [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
		  },
		  {
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
		  },
		  {
				  "fieldname":"party_type",
				  "label": __("Party Type"),
				  "fieldtype": "Link",
				  "options": "DocType",
				  "get_query": function() {
					  return {
						  filters: {"name": ["in", ["Customer", "Supplier"]]}
					  }
				  },
			on_change: () => {
			  frappe.query_report.set_filter_value("party", ' ');
					  frappe.query_report.refresh();
			},
			  },
		  {
			fieldname: "party",
			label: __("Party"),
			fieldtype: "Dynamic Link",
			// options: "party_type",
			"get_options": function() {
					  var applicant_type = frappe.query_report.get_filter_value('party_type');
					  var applicant = frappe.query_report.get_filter_value('party');
					  if(applicant && !applicant_type) {
						  frappe.throw(__("Please select Party Type first"));
					  }
					  return applicant_type;
				  }
		  },  
		  {
			fieldname: "payment",
			label: __("Payment Entry"),
			fieldtype: "Link",
			options: "Payment Entry",
		  },
		  {
			fieldname: "current_state",
			label: __("Current State"),
			fieldtype: "Select",
			options: [
				"",
				"New",
				"Under Collect",
				"Rejected",
				"Rejected in Bank",
				"Collected",
				"Endorsed",
				"Paid",
			  ],
		  },
	]
};
