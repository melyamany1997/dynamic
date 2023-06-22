// Copyright (c) 2022, Dynamic and contributors
// For license information, please see license.txt

frappe.ui.form.on('Item Request', {
	// item_group(frm){
	// 	if(frm.doc.item_group && frm.doc.__islocal){
	// 		frappe.call({
	// 			method:'dynamic.api.generate_item_code',
	// 			args:{
	// 				'item_group':frm.doc.item_group
	// 			},callback(r){
	// 				if(r.message){
	// 					if(r.message == 'false'){
	// 						frm.set_value("item_group","")
	// 						frm.refresh_field('item_group')
	// 					}else{
	// 					frm.set_value('item_code',r.message)
	// 					frm.refresh_field('item_code')
	// 					}
	// 				}
	// 			}
	// 		})
	// 	}
	// },
	validate:(frm)=>{
		let bext = $('.primary-action').text();
		if(bext != "Save"){
		$('.primary-action').prop('hidden', true);
		}
	},
	 refresh: function(frm) {
		//console.log("assssssssssssssssssssss",frm.doc.name);
		let bext = $('.primary-action').text();
		if(bext == "Submit"){
			$('.primary-action').prop('hidden', true);
			}
		if (!frm.doc.__islocal && frm.doc.request_status!="approved"){
			$('.primary-action').prop('hidden', true);
			frappe.call({
				method:"can_approve_item",
				doc:frm.doc,
				callback(r){
					if(frappe.user.has_role(r.message)){
						frm.add_custom_button(__('Approve'), () => frm.events.approve_item_request(frm));
					}
				}
			})
		}
	 },
	 approve_item_request:(frm)=>{
		// let d = new frappe.ui.Dialog({
		// 	title: 'Enter details',
		// 	fields: [
		// 		{
		// 			label: 'Standart Selling Rate',
		// 			fieldname: 'standard_rate',
		// 			fieldtype: 'Currency',
		// 			reqd:1
		// 		}
		// 	],
		// 	primary_action_label: 'Submit',
		// 	primary_action(values) {
		// 		//console.log(values.standard_rate);
		// 		frm.set_value("standard_rate",values.standard_rate);
		// 		frm.set_value("request_status","approved");
		// 		d.hide();
		// 		//frm.save();
		// 		//frm.doc.docstatus=1;
		// 		//frm.submit();
		// 		// frm.save()
		// 		frappe.call({
		// 			"method": "frappe.client.submit",
		// 			"args": {
		// 				  "doctype": "Item Request",
		// 				  "docname":frm.doc.name,
		// 				  "doc": frm.doc
		// 			},callback(r){
		// 				frm.reload_doc();
		// 				//frm.refresh_field("docstatus");
		// 				//cur_frm.refresh();
		// 				//frm.reload();
		// 			}
		// 		})
				
				
		// 	}
		// });
		
		// d.show();
		frm.set_value("request_status","approved");
		frappe.call({
			"method": "frappe.client.submit",
			"args": {
				  "doctype": "Item Request",
				  "docname":frm.doc.name,
				  "doc": frm.doc
			},callback(r){
				frm.reload_doc();
				//frm.refresh_field("docstatus");
				//cur_frm.refresh();
				//frm.reload();
			}
		})
	 }
});
