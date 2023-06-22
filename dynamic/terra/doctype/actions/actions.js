// Copyright (c) 2022, Dynamic and contributors
// For license information, please see license.txt

frappe.ui.form.on('Actions', {
	refresh:(frm)=>{
		if(!frm.doc.__islocal){
			frm.add_custom_button(
			  __("Show History"),
			  function () {
				frappe.set_route('query-report','Actions Report',{"phone_no":frm.doc.phone_no})
			  }
			);
	}
	},
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
