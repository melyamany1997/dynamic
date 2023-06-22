// Copyright (c) 2022, Dynamic and contributors
// For license information, please see license.txt


frappe.ui.form.on('Car', {
	// refresh: function(frm) {

	// }
	setup:function(frm){
		frm.set_query('serial_no',(doc)=>{
			return {
				query: 'dynamic.gebco.doctype.car.car.get_serial_no_query',
				filters:{"docname":frm.doc.name}
			}
			
		})
	}
});
