


frappe.listview_settings['Reservation'] = {
	add_fields: ["base_grand_total", "company", "currency", "supplier",
		"supplier_name", "per_received", "per_billed", "status"],
	get_indicator: function (doc) {
		if (doc.status === "Closed") {
			return [__("Closed"), "green", "status,=,Closed"];
		} else if (doc.status === "Active") {
			return [__("Active"), "orange", "status,=,Active"];
		} else if (doc.status === "Invalid") {
			return [__("Invalid"), "red", "status,=,Invalid"];
		}  else if (doc.status === "Partial Delivered") {
		return [__("Partial Delivered"), "blue", "status,=,Partial Delivered"];
		} 

	},
};
