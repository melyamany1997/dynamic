// Copyright (c) 2023, Dynamic and contributors
// For license information, please see license.txt

frappe.ui.form.on('test_ifi', {
	refresh: function(frm) {
		frm.add_custom_button("print22",()=>{
			frappe.route_options = {
				frm: frm,
			};
			frappe.set_route('print', frm.doc.doctype, frm.doc.name);
		})
	}
});
