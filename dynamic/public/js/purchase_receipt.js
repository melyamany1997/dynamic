

frappe.ui.form.on('Purchase Receipt', {
	onload: function(frm) {
        frappe.call({
            method: "dynamic.api.get_active_domains",
            callback: function (r) {
                if (r.message && r.message.length) {
                    if (r.message.includes("Terra")) {
                        if(frm.is_new()){
                            if(frm.doc.items){
                                frm.doc.items.forEach(row => {
                                    row.qty = 1
                                });
                                frm.refresh_field("items")
                            }
                        }
                    }
                }
            }
        })
	}
});