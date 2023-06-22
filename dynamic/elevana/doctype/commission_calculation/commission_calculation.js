// Copyright (c) 2023, Dynamic and contributors
// For license information, please see license.txt

frappe.ui.form.on('Commission Calculation', {
	refresh: function(frm) {
		frm.add_custom_button("Calculate",()=>{
			frm.events.calculate_commission(frm)
		})
	},
	calculate_commission:function(frm){
		if(frm.doc.commission_date){
			frm.call({
				method:"dynamic.elevana.doctype.commission_calculation.commission_calculation.calculate_commission",
				args:{
					"commission_date":frm.doc.commission_date,
					"sales_person":frm.doc.sales_person
				},
				callback:function(r){
					if(!r.exp && r.message){
						frm.set_value("commission_info",[])
						// console.log(r.message)
						$.each(r.message || [], function(i, item){
							let row = frm.add_child('commission_info', {
								sales_person: item.sales_person,
								sales: item.invoice_amount,
								return: item.return_invoice,
								total: (item.invoice_amount+item.return_invoice),
								incentives: item.incentives || 0,
								commission_date:frm.doc.commission_date
							});
							
							frm.refresh_field('commission_info');
						})
					}
				}
			})
		}
	}
});
