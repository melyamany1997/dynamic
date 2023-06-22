


frappe.ui.form.on('Mode of Payment', {  
	refresh: function(frm) {
        if(frm.doc.docstatus == 0 && frm.doc.__islocal != 1) 
        frm.add_custom_button(
            __("Show Ledger"),
            function () {
                frappe.set_route('query-report','Mode Of Payment Report',{"mode_of_payment":frm.doc.name,"make_hidden":1})

            },
            __("Show")
          );
	},

    
});