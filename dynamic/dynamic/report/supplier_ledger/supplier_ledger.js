// Copyright (c) 2023, Dynamic and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Supplier Ledger"] = {
	"filters": [
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
		{
			label: __("Party Type"),
			fieldname:"party_type",
			fieldtype: "Select",
			options: 'Customer\nSupplier',
			default:"Customer",
			reqd: 1,
			on_change: function() {
						frappe.query_report.set_filter_value('party', "");
					}
		},
		{
			label: __("Party"),
			fieldname:"party",
			fieldtype: "Dynamic Link",
	  		get_options: function() {
				var party_type = frappe.query_report.get_filter_value('party_type');
				var party = frappe.query_report.get_filter_value('party');
				if(party && !party_type) {
					frappe.throw(__("Please select Party Type first"));
				}
				return party_type;
			}
		},
		{
			label: __("Currency"),
			fieldname:"currency",
			fieldtype: "Link",
	  		options: 'Currency'
		}
	]
};
