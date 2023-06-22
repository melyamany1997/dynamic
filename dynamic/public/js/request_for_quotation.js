frappe.ui.form.on("Request for Quotation", {
    get_stock_uom:function(frm){
        if (frm.doc.items) {
            frappe.call({
                method: "dynamic.api.get_active_domains",
                callback: function (r) {
                    if (r.message && r.message.length) {
                        if (r.message.includes("IFI")) {
                            frm.doc.items.forEach(element => {
                                if(element.item_code){
                                    frappe.run_serially([
                                        () => {
                                            frappe.call({
                                                method:"frappe.client.get_value",
                                                args:{
                                                    doctype:"Item",
                                                    fieldname:"stock_uom",
                                                    "filters": {
                                                        'name': element.item_code,
                                                      
                                                      },
                                                },
                                                callback:function(r){
                                                    element.stock_uom = r.message.stock_uom
                                                }
                                            })
                                        },
                                        () => {
                                            frappe.call({
                                                method:"frappe.client.get_single_value",
                                                args:{
                                                    doctype:"Stock Settings",
                                                    field:"default_warehouse",
                                                },
                                                callback:function(r){
                                                    element.warehouse  = r.message
                                                }
                                            })
                                        }
                                    ])
                                    
                                }
                                frm.refresh()
                            });
                        }
                    }
                }
            })
        }
    }
})




frappe.ui.form.on("Request for Quotation Supplier", {
	suppliers_add(frm, cdt, cdn) {
        let supp_row  = locals[cdt][cdn]
        if (supp_row.supplier){
            frm.events.get_stock_uom(frm)
        }
	},

    supplier:function(frm,cdt,cdn){
        let supp_row  = locals[cdt][cdn]
        if (supp_row.supplier){
            frm.events.get_stock_uom(frm)
        }
    }
});