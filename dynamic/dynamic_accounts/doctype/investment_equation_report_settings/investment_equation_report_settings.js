// Copyright (c) 2023, Dynamic and contributors
// For license information, please see license.txt

frappe.ui.form.on('Investment Equation Report Settings', {
	setup: function (frm) {
		frm.set_query("account", "assets", function () {
			return {
				filters: [
					["company", "=", frm.doc.company],
					["is_group", "=", 0],
					["disabled", "=", 0],
					["root_type", "=", "Asset"],
				],
			};
		});
		frm.set_query("account", "equity", function () {
			return {
				filters: [
					["company", "=", frm.doc.company],
					["is_group", "=", 0],
					["disabled", "=", 0],
					["root_type", "=", "Equity"],
				],
			};
		});
	}
	// refresh: function(frm) {

	// }
});
