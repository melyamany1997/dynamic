
frappe.ui.form.on("Customer", {
    check_url: function (frm) {
        if (frm.doc.url) {
            frappe.call({
                method: "dynamic.api.get_active_domains",
                callback: function (r) {
                    if (r.message && r.message.length) {
                        if (r.message.includes("IFI")) {
                            window.open(frappe.model.scrub(frm.doc.url));
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
                        frm.add_custom_button(
                            __("Appointment"),
                            function () {
                                frm.events.create_cst_appointment(frm)
                            },
                            __("Create")
                        );
                    }
                    if(r.message.includes("CRM Advance")){
                        if(!frm.doc.__islocal){
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
    create_cst_appointment:function(frm){
        frappe.model.open_mapped_doc({
            method:
                "dynamic.terra.api.create_cst_appointment",
            frm: frm,
        });
    }
})