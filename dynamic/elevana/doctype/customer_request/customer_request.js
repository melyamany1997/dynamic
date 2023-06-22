// Copyright (c) 2023, Dynamic and contributors
// For license information, please see license.txt

frappe.ui.form.on('Customer Request', {
	// refresh: function(frm) {

	// }
	onload(frm) {
		let required_fields = [
			"customer_name",
			"phone_number",
			"email",
			"tax_id",
			"tax_register_number",
			"com_id",
			"city",
			"country",
			"address_line",
		]
		required_fields.forEach((field) => {
			frm.set_df_property(field, "reqd", frm.doc.docstatus == 0)
		})
	}
});
