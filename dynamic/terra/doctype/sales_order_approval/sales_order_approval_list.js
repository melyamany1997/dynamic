frappe.listview_settings['Sales Order Approval'] = {
	get_indicator: function (doc) {
		if (doc.status == "Draft"){
			return [__("Draft"), "red", "status,=,Draft"];
		}
		else if(doc.status == "To Deliver"){
			return [__("To Deliver"), "orange", "status,=,To Deliver"];
		}
		else if (doc.status === "Partial Delivered") {
			// Closed
			return [__("Partial Delivered"), "green", "status,=,Partial Delivered"];
		} else if (doc.status === "Completed") {
			// on hold
			return [__("Completed"), "green", "status,=,Completed"];
		}
	}
};
