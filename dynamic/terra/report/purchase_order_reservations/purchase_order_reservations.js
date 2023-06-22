// Copyright (c) 2022, Dynamic and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Purchase Order Reservations"] = {
	"filters": [
		{
			fieldname: "puchase_order",
			label: __("Purchase Order"),
			fieldtype: "Link",
			options:"Purchase Order"
		},
	] 
};
