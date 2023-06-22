


frappe.ui.form.on("Delivery Note", {
    domian_valid: function (frm) {
        var tera = false
       frappe.call({
             method :"dynamic.dynamic.validation.get_active_domain_gebco" ,
             async: false,
             callback:function (r){
                 if (r.message) {
                     tera = true
                 }else {
                     tera = false
                 }
             }
         })
      return tera
 
     } ,
     onload(frm) {
        var check_domain = frm.events.domian_valid()
        if (check_domain && frm.doc.docstatus == 0) {
            frm.add_custom_button(
              __("view Item Shortage"),
              function () {
                frappe.call({
                  method:
                    "dynamic.api.validate_active_domains_note",
                  args: {
                    doc: frm.doc.name ,
                  },
                  callback: function (r) {
                     console.log(r.message);
                    
                    // socket(JSON.stringify(data));
                  },
                });
              },
              "view Item Shortage"
            );
          }

     } ,  
    
})





