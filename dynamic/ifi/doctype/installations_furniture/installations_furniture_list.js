frappe.listview_settings['Sales Order'] = {
	add_fields: ["status"],
	get_indicator: function (doc) {
		if (doc.status === "Pending") {
			return [__("Pending"), "green", "status,=,Pending"];
		} else if (doc.status === "Start") {
			return [__("Start"), "orange", "status,=,Start"];
		} else if (doc.status === "Inprogress") {
			return [__("Inprogress"), "blue", "status,=,Inprogress"];
        }else if (doc.status === "Completed") {
			return [__("Completed"), "orange", "status,=,Completed"];
        }
    }
}