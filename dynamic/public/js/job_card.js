

frappe.ui.form.on("Job Card", {
    refresh:function(frm){
        if(frm.doc.docstatus === 1){
            frm.add_custom_button(
                __("Show Line"),
                function () {
                  frappe.set_route('query-report','Line Paramter Report',{"dt":frm.doc.doctype , "dn2":frm.doc.name})
                }
              );
        }
    }
})