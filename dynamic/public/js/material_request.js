frappe.ui.form.on("Material Request",{
    refresh(frm){
        frm.events.trea_setup(frm)
    },
    trea_setup(frm){
        frappe.call({
          method:"dynamic.api.validate_terra_domain",
          callback:function(r) {
            if (r.message){
              frm.events.make_custom_buttons_2(frm)
            }
          }
         })
    
      },
    make_custom_buttons_2: function(frm) {
        if (frm.doc.docstatus==1) {
            if (frm.doc.material_request_type === "Price Request") {
                frm.add_custom_button(__("Request for Quotation"),
                    () => frm.events.make_request_for_quotation_2(frm), __('Create'));
            }
            if (frm.doc.material_request_type === "Price Request") {
            frm.add_custom_button(__("Supplier Quotation"),
            () => frm.events.make_supplier_quotation_2(frm), __('Create')); }
        }
    },
    make_supplier_quotation_2: function(frm) {
		frappe.model.open_mapped_doc({
			method: "dynamic.terra.doctype.supplier_quotation.supplier_quotation.make_supplier_quotation",
			frm: frm
		});
    
    },
    make_request_for_quotation_2: function(frm) {
		frappe.model.open_mapped_doc({
			method: "dynamic.terra.doctype.supplier_quotation.supplier_quotation.make_request_for_quotation",
			frm: frm,
			run_link_triggers: true
		});
	},
  
    
    
})
