// Copyright (c) 2022, Dynamic and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Actions Report"] = {
	// asd
	"filters": [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date"
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date"
		},
		{
			fieldname: "type",
			label: __("Type"),
			fieldtype: "Select",
			options:"\nIndoor\nOut door"
		},
		{
			fieldname: "actions",
			label: __("Action"),
			fieldtype: "Link",
			options:"Action"
		},
		{
			fieldname: "phone_no",
			label: __("Phone No"),
			fieldtype: "Data"
		},
		// {
		// 	fieldname: "customer_type",
		// 	label: __("Customer Type"),
		// 	fieldtype: "Select",
		// 	options:"\nLead\nOpportunity\nCustomer",
		// 	on_change: function() {
		// 		frappe.query_report.set_filter_value('cusomer', "");
		// 	}
		// },
		// {
		// 	fieldname: "cusomer",
		// 	label: __("Customer"),
		// 	fieldtype: "MultiSelectList",
		// 	get_data: function(txt) {
		// 		if (!frappe.query_report.filters) return;

		// 		let party_type = frappe.query_report.get_filter_value('customer_type');
		// 		if (!party_type) return;

		// 		return frappe.db.get_link_options(party_type, txt);
		// 	},
		// },
		{
			fieldname: "branch",
			label: __("Branch"),
			fieldtype: "Link",
			options:"Branch"
		}
	]
};

