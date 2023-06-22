// Copyright (c) 2023, Dynamic and contributors
// For license information, please see license.txt

frappe.ui.form.on('Coupon Group', {
	// refresh: function(frm) {

	// }
	setup: function (frm) {
		frm.set_query("pricing_rule", function () {
			return {
				filters: [
					["Pricing Rule", "coupon_code_based", "=", "1"]
				]
			};
		});
	},
});
