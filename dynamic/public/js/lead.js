
frappe.provide("erpnext");

frappe.ui.form.on("Lead", {
    check_url: function (frm) {
        if (frm.doc.url) {
            frappe.call({
                method: "dynamic.api.get_active_domains",
                callback: function (r) {
                    if (r.message && r.message.length) {
                        if (r.message.includes("IFI")) {
                            window.open(frappe.model.scrub(frm.doc.url));
                        }
                        if (r.message.includes("Terra") || r.message.includes("Elevana") ) {
                            frm.add_custom_button(
                                __("Action"),
                                function () {
                                    frappe.call({
                                        method: "terra.api.create_action_doc",
                                        args: {
                                            doctype: frm.doc.doctype,
                                            docname: frm.doc.name
                                        },
                                        callback: function (r) {
                                            if (r.message) {
                                                frappe.set_route("Form", r.message.doctype, r.message.name);
                                            }

                                        }
                                    });
                                },
                                __("Create")
                            ).addClass("btn-primary");
                        }
                    }
                }
            })
        }
    },
    refresh(frm) {
        frappe.call({
            method: "dynamic.api.get_active_domains",
            callback: function (r) {
                if (r.message && r.message.length) {
                    if (r.message.includes("Terra") || r.message.includes("Elevana") || r.message.includes("CRM Advance")) {
                        frm.add_custom_button(
                            __("Action"),
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
                        frm.add_custom_button(__("Make Sales Order"),function () {
                            frm.events.make_customer_sales_order_from_lead(frm)
                        }, __("Create"))
                    }
                    if(r.message.includes("CRM Advance")){
                            if(!frm.doc.__islocal){
                               frm.add_custom_button(
                            __("New Appointment"),
                            function () {
                              frappe.model.open_mapped_doc({
                                method:"dynamic.api.create_new_appointment",
                                frm: frm
                              });
                            },
                            __("Create")
                          );
                          frm.add_custom_button(
                            __("Show History"),
                            function () {
                              frappe.set_route('query-report','Actions Report',{"phone_no":frm.doc.phone_no})
                            }
                          );
                            }
                    }
                }
            }
        })
    },
    make_customer_sales_order_from_lead:function(frm){
        frappe.model.open_mapped_doc({
            method: "dynamic.terra.doctype.quotation.quotation.make_sales_order_lead",
            frm: cur_frm
        })
    },
    make_opportunity(frm) {
        frappe.model.open_mapped_doc({
            method: "dynamic.ifi.api.make_opportunity",
            frm: cur_frm
        })
    },
    make_quotation_elevana(frm) {
        frappe.model.open_mapped_doc({
            method: "dynamic.elevana.api.make_quotation",
            frm: cur_frm
        })
    }
})



const LeadController_Extend = erpnext.LeadController.extend({

    refresh: function (frm) {
        this._super()
        // let doc = this.frm.doc
        frappe.call({
            method: "dynamic.api.get_active_domains",
            callback: function (r) {
                if (r.message && r.message.length) {
                    if (r.message.includes("IFI")) {
                        if (!frm.__islocal && frm.__onload && !frm.__onload.is_customer) {
                            cur_frm.page.remove_inner_button('Opportunity', 'Create')
                            cur_frm.add_custom_button(__("Opportunity"), function () {
                                cur_frm.events.make_opportunity(cur_frm)
                            }, __("Create"));
                        }
                    }
                    if (r.message.includes("Elevana")) {
                        if (!frm.__islocal && frm.__onload && !frm.__onload.is_customer) {
                            cur_frm.page.remove_inner_button('Quotation', 'Create')
                            cur_frm.add_custom_button(__("Quotation"), function () {
                                cur_frm.events.make_quotation_elevana(cur_frm)
                            }, __("Create"));
                        }
                    }
                }
            }
        })


    },


})

$.extend(
    cur_frm.cscript,
    new LeadController_Extend({ frm: cur_frm }),
);

var create_ifi_sales_order = function () {

    frappe.model.open_mapped_doc({
        method: "dynamic.ifi.api.make_sales_order",
        frm: cur_frm
    })
}