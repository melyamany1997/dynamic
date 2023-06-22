
frappe.ui.form.on("Opportunity", {

    refresh(frm) {
        frappe.call({
            method: "dynamic.api.get_active_domains",
            callback: function (r) {
                if (r.message && r.message.length) {
                    if (r.message.includes("Terra") || r.message.includes("CRM Advance")) {
                        frm.add_custom_button(
                            __("Action","Elevana"),
                            function () {
                                frappe.model.open_mapped_doc({
                                    method:
                                        "dynamic.terra.api.create_action_doc",
                                    frm: frm,
                                    args: {
                                        doctype: frm.doc.doctype,
                                    }
                                });
                            },
                            __("Create")
                        );
                    }
                    if (r.message.includes("IFI")) {
                        cur_frm.cscript['create_quotation'] = create_quotation
                    }
                    if(r.message.includes("CRM Advance")){
                            if(!frm.doc.__islocal){
                                frm.add_custom_button(
                                  __("Show History"),
                                  function () {
                                    frappe.set_route('query-report','Actions Report',{"phone_no":frm.doc.phone_no})
                                  }
                                );
                                frm.add_custom_button(__('Make Sales Order'),
                                  function() {
                                      frm.trigger("make_sales_order")
                                  }, __('Create'));
                                  
                                  frm.add_custom_button(__('Make Material Request'),
                                  function() {
                                      frm.trigger("make_material_request")
                                  }, __('Create'));
                                  }
                    }
                }
            }
        })
    },

    make_sales_order:function(frm){
        frappe.model.open_mapped_doc({
            method:"dynamic.terra.api.create_sales_order_from_opportunity",
            frm:frm
        })
    },
    make_material_request:function(frm){
        frappe.model.open_mapped_doc({
            method:"dynamic.terra.api.create_material_request_from_opportunity",
            frm:frm
        })
    }
})

var create_quotation = function() {
    frappe.model.open_mapped_doc({
		method: "dynamic.ifi.api.make_quotation",
		frm: cur_frm
	})
}

var make_material_request = function() {
    frappe.model.open_mapped_doc({
		method: "dynamic.terra.doctype.api.make_material_request",
		frm: cur_frm
	})
}