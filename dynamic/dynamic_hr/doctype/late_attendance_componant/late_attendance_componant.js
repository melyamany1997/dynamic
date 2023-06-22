// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Late Attendance Componant', {
	// refresh: function(frm) {

	// }
	onload:function(frm){
		if (frm.doc.add_deduction == 0){
		
				frm.set_df_property('deduction_factors' , 'hidden' ,1);
				frm.refresh_field('deduction_factor')
		}else{
			frm.set_df_property('deduction_factor' , 'hidden' ,0);
			frm.refresh_field('deduction_factor')
		}

	},
	add_deduction:function(frm){
				if (frm.doc.add_deduction == 0){
		
				frm.set_df_property('deduction_factors' , 'hidden' ,1);
						frm.refresh_field('deduction_factor')
				}else{
					frm.set_df_property('deduction_factor' , 'hidden' ,0);
					frm.refresh_field('deduction_factor')
				}


	}
});
