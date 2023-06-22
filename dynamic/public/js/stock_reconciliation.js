

frappe.ui.form.on("Stock Reconciliation", {

    refresh(frm) {
        frappe.call({
            method: "dynamic.api.get_active_domains",
            callback: function (r) {
                if (r.message && r.message.length) {
                    if (r.message.includes("Terra")) {
                        frm.events.set_queries_terra(frm)
                    }
                }
            }
        })
    },
    set_queries_terra(frm) {
        frm.set_query('item_code','items', function(doc,cdt,cdn) {
            let row = locals[cdt][cdn]
            return{
                query: "dynamic.terra.api.get_item_group_brand",
                filters: { 
                    'item_group': row.item_group,
                    'brand': row.brand ,
                 }
               }
            })
    },

})




