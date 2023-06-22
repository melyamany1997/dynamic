frappe.ui.form.on("Quotation",{
    // onload:function(frm) {
    //     frm.events.refresh(frm)
    // },
    refresh:function(frm){
        frappe.call({
            method: "dynamic.api.get_active_domains",
            callback: function (r) {
              if (r.message && r.message.length) {
                if (r.message.includes("Terra")) {
                    cur_frm.cscript['Make Sales Order'] = create_terra_sales_order
                    if (frm.doc.docstatus == 1) {
                        if (frm.doc.quotation_to == "Lead"){
                            frappe.db.get_value("Customer", {"lead_name": frm.doc.party_name}, "name", (r) => {
                                if(!r.name){
                                cur_frm.add_custom_button(__('Customer'),function(){
                                    frappe.call({
                                        method:"dynamic.terra.doctype.quotation.quotation.make_customer",
                                        args:{
                                            source_name:frm.doc.name,
                                        },
                                        callback:function(r){
                                            frm.refresh()
                                        }
        
                                    })
                                }
                                , __('Create'));	 
                                }						
                            });
                            }
                        cur_frm.add_custom_button(__('Payment Entry'),
                                cur_frm.cscript['Make Payment Entry'], __('Create'));
                       
                    }
                }
                if (r.message.includes("IFI")) {
                    if(frm.doc.docstatus == 1){
                        frm.add_custom_button("Potential",()=>{
                            frappe.confirm('Are you sure you want to Potential quotation',
                                () => {
                                    frappe.call({
                                        method:"dynamic.ifi.api.set_potential_status",
                                        args:{
                                            frm_name:frm.doc.name,
                                        },
                                        callback:function(r){
                                             frm.refresh()
                                        }
            
                                    })
                                }, () => {
                                    // action to perform if No is selected
                                })
    
                        })
                    }
                    
                    
               
                };
                   
            }
        }
    })
    },
    reject_quotation(frm){
        frm.call({
            method:"dynamic.ifi.doctype.installations_furniture.installations_furniture.reqject_quotation",
            args:{
                source_name:frm.doc.name, 
            },
            callback:function(r){
                frm.reload_doc()
            }

        })
    },

 
})



const QuotationController_Extend = erpnext.selling.QuotationController.extend({
  
	refresh: function(doc, dt, dn) {
		this._super(doc);
        frappe.call({
            method: "dynamic.api.get_active_domains",
            callback: function (r) {
              if (r.message && r.message.length) {
                if (r.message.includes("IFI")) {
                    cur_frm.page.remove_inner_button('Subscription','Create')
                    cur_frm.cscript['Make Sales Order'] = create_ifi_sales_order
                    // cur_frm.cscript['Make Payment Entry'] = create_ifi_payment_entry
                    if(doc.docstatus == 1 && doc.status!=='Lost') {
                        if(!doc.valid_till || frappe.datetime.get_diff(doc.valid_till, frappe.datetime.get_today()) >= 0) {
                            cur_frm.page.remove_inner_button('Sales Order','Create')
                            cur_frm.add_custom_button(__('Sales Order'),
                                cur_frm.cscript['Make Sales Order'], __('Create'));
                        }
                    }
                }
              }
            }
            })
        

	},
})

$.extend(
	cur_frm.cscript,
	new QuotationController_Extend({frm: cur_frm}),
);

var create_ifi_sales_order = function() {

    frappe.model.open_mapped_doc({
		method: "dynamic.ifi.api.make_sales_order",
		frm: cur_frm
	})
}

var create_terra_sales_order = function() {

    frappe.model.open_mapped_doc({
		method: "dynamic.terra.doctype.quotation.quotation.make_sales_order",
		frm: cur_frm
	})
}





// var create_ifi_payment_entry = function() {
//     frappe.model.open_mapped_doc({
//         method:
//         "dynamic.terra.api.get_payment_entry_quotation",
//         frm: cur_frm,
//       });
// }



cur_frm.cscript['Make Payment Entry'] = function() {
    frappe.model.open_mapped_doc({
        method:
        "dynamic.terra.api.get_payment_entry_quotation",
        frm: cur_frm,
      });
}
