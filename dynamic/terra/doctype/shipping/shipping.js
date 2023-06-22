// Copyright (c) 2022, Dynamic and contributors
// For license information, please see license.txt

frappe.ui.form.on('Shipping', {
	 refresh: function(frm) {
		frm.set_query("shipping_account", function () {
			return {
			  filters: [
				["is_group", "=", 0],
				["disabled", "=", 0],
			  ],
			};
		  });
		  frm.set_query("cost_center", function () {
			return {
			  filters: [
				["is_group", "=", 0],
				["disabled", "=", 0],
			  ],
			};
		  });
	 }

});
