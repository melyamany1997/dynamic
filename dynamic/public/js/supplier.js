

frappe.ui.form.on("Supplier", {
    check_url:function(frm){
        if(frm.doc.url){
            frappe.call({
                method: "dynamic.api.get_active_domains",
                callback: function (r) {
                  if (r.message && r.message.length) {
                    if (r.message.includes("IFI")) {
                        window.open(frappe.model.scrub(frm.doc.url));
                    }
                }}
            })
        }
    }
})