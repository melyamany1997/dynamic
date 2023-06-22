// Copyright (c) 2022, Dynamic and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Commision Report"] = {
	"filters": [
		  {
			fieldname: "sales_person",
			label: __("Sales Person"),
			fieldtype: "Link",
			options: "Sales Person",
		  },
		  {
			fieldname: "sales_invoice",
			label: __("Sales Invoice"),
			fieldtype: "Link",
			options: "Sales Invoice",
		  },
		  {
			fieldname: "item_group",
			label: __("Item Group"),
			fieldtype: "Link",
			options: "Item Group",
		  },
		  {
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date"
		  },
		  {
			fieldname: "to_date",
			label: __("To date"),
			fieldtype: "Date"
		  }
	]
};
