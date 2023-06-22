// Copyright (c) 2023, Dynamic and contributors
// For license information, please see license.txt

frappe.ui.form.on('Phone Call', {
	refresh: function (frm) {
		if (!frm.is_new()) {
			if (!(frm.doc.customer || frm.doc.lead)) {
				frm.add_custom_button(
					__("Customer"),
					function () {
						frappe.model.open_mapped_doc({
							method:
								"dynamic.elevana.doctype.phone_call.phone_call.create_customer",
							frm: frm,
						});
					},
					__("Create")
				);
				frm.add_custom_button(
					__("Lead"),
					function () {
						frappe.model.open_mapped_doc({
							method:
								"dynamic.elevana.doctype.phone_call.phone_call.create_lead",
							frm: frm,
						});
					},
					__("Create")
				);
			}
		}

	}
});
