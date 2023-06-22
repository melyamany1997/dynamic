// Copyright (c) 2022, Dynamic and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Employee Schedule"] = {
	"filters": [
		{
			fieldname: "from_time",
			label: __("From Time"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1
		  },
		  {
			fieldname: "to_time",
			label: __("To time"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1
		  },
		  {
			fieldname:"employee",
			label:__("Employee"),
			fieldtype:"Link",
			options:"Employee"
		  },
		  {
			fieldname:"team",
			label:__("Team"),
			fieldtype:"Link",
			options:"Installation Team"
		  },
		  {
			fieldname:"installation_order",
			label:__("Installation Order"),
			fieldtype:"Link",
			options:"Installation Order"
		  },
		  {
			fieldname:"installation_request",
			label:__("Installation Request"),
			fieldtype:"Link",
			options:"Installation Request"
		  }
	]
};
