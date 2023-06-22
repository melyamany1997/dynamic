// Copyright (c) 2022, Dynamic and contributors
// For license information, please see license.txt

frappe.ui.form.on('Actions', {
	type: function(frm) {
		frm.events.filter_actions(frm)
	},

	filter_actions:(frm)=>{
		frm.set_query("action", function (doc) {
			return {
			  filters: {
				type: frm.doc.type
			  },
			};
		  });
	}
});
