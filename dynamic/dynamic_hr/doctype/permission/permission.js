// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Permission', {
	  	refresh:function(frm){
		// if(frm.doc.docstatus =='0' &&frm.doc.date !=null){
		//       frm.page.clear_primary_action();
		//         frappe.call({
        //         //method: "erpnext.hr.doctype.mission.mission.updateStaus",
        //         method:'updateStaus',
        //         doc:frm.doc,
        //         callback(r) {
        //         	console.log(r.message)
        //             if (r.message!="false") {
        //                frm.add_custom_button(__(r.message),function(){
        //                	 //frm.event.updateAction(r.message);
        //                  	  frappe.call({
		// 		                method:'updateAction',
		// 		                doc:frm.doc,
		// 		                args:{
		// 		                   'Action':r.message
		// 		                },callback(r) {
		//
		// 		                	frm.page.clear_primary_action();
		// 		                	frm.refresh();
		// 		                }
		//
		// 		            });
		//
        //                }).addClass('btn-primary')
		//
        //             }
        //         }
        //     });
		//   }
		//   frm.events.checkIfHasRoleSubmit(frm)
	},

		checkIfHasRoleSubmit(frm){
			if(frm.doc.docstatus =='0' &&frm.doc.date !=null){
		     frm.page.clear_primary_action();
				frappe.call({
                
                method:'checkIfHasRoleSubmit',
                doc:frm.doc,
                callback(r) {
                    if (r.message=="true") {
                    	
                       frm.add_custom_button(__("Submit"),function(){
                       	   	  frappe.call({
				                method:'Submitdoctype',
				                doc:frm.doc,
				                args:{
				                   'Action':'Approved'
				                },callback(r) {
				                	
				                	frm.page.clear_primary_action();
				                	frm.refresh();
				                }
				              
				            });
                         
                       }).addClass('btn-primary')

                    }
                   
                }
            });
			}
	},

});
