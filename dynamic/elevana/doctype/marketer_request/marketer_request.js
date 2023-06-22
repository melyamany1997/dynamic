// Copyright (c) 2023, Dynamic and contributors
// For license information, please see license.txt

frappe.ui.form.on('Marketer Request', {
	// refresh: function(frm) {

	// }
	onload(frm) {
		let required_fields = [
			"marketer_name",
			"phone_number",
			"email",
			"partner_type",
			"commission_rate",
			"city",
			"country",
			"address_line",
			"item_groups"
		]
		required_fields.forEach((field) => {
			frm.set_df_property(field, "reqd", frm.doc.docstatus == 0)
		})
	}
});
