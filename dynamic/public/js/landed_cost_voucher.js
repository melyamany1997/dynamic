frappe.ui.form.on("Landed Cost Voucher", {

    domian_valid: function (frm) {
       var tera = false
      frappe.call({
            method :"dynamic.dynamic.validation.get_active_domain" ,
            async: false,
            callback:function (r){
                if (r.message) {
                    tera = true
                    console.log("terra Active")
                }else {
                    tera = false
                }
            }
        })
     return tera

    } ,
    set_up_jebco_query(frm){
        
        frm.set_query("doc_type", "cost_child_table", () => {
            return {
                query :"dynamic.dynamic.validation.get_query_type"
            };
        })
    },
    setup_child_querys(frm){
        frm.fields_dict.cost_child_table.grid.get_field('invoice').get_query =
        function(doc,cdt,cdn) {
			var d = locals[cdt][cdn]
            if (d.doc_type == "Purchase Invoice") {
                return {
                    query : "dynamic.dynamic.validation.get_purchase_items"
                }

            }
         
            return {
                filters: filters
            }
        }
    },
    refresh: function(frm) {  
        // Check If Jebco in Active Domains 
        // This Function will Do Dothing 
        var check_domain = frm.events.domian_valid()
        if (check_domain){
            frm.events.set_up_jebco_query(frm)
            frm.events.setup_child_querys(frm)
        }
    } ,
    add_row_to_charges(frm , data){
        data.forEach(element => {
            console.log("element" ,element.line_name)
            var raw = frm.add_child("taxes")
            raw.expense_account = element.account
            raw.description = element.description
            raw.amount = element.amount
            raw.line_name = element.line_name
            raw.docment_type = element.docment_type
            raw.docment_name = element.document
            
        });
        frm.refresh_field("taxes")
    },
    set_applicabel_charges:function(frm){
        frm.clear_table("taxes")
        frm.refresh_field("taxes")
        var i = 0 

       
        for (i = 0 ; i < frm.doc.cost_child_table.length ; i ++ ){
           
            // frm.events.add_row_to_charges(frm,frm.doc.cost_child_table[i].doc_type , frm.doc.cost_child_table[i].invoice )
            frappe.call({
                method:"dynamic.terra.landed_cost.get_line_info",
                async: false,
                args :
                {
                    "allocated_amount" : frm.doc.cost_child_table[i].allocated_amount ,
                    "doc_type": frm.doc.cost_child_table[i].doc_type,
                    "document": frm.doc.cost_child_table[i].invoice
                } ,
                callback:function(r){
                    console.log(r)
                    frm.events.add_row_to_charges(frm ,r.message)
                }
            })
        
        }
    },
  


})


frappe.ui.form.on('Landed Cost Voucher Child', {
    doc_type:function(frm ,cdt,cdn){
        frm.events.setup_child_querys(frm)
    },
    invoice:function(frm , cdt,cdn){
       var  local = locals[cdt][cdn]
       var doc_ument =  local.invoice
       var doctype = local.doc_type
        if (frm.doc.cost_child_table.length > 1 ){
            var count = frm.doc.cost_child_table.filter(
                x=> x.invoice==doc_ument
            ).length
            if(count > 1){
                local.invoice = ''
                frm.refresh_field("cost_child_table")
                frappe.throw("Duplicated Invocie Not allowed")
                
            }

            
        } 

       frappe.call({
           method:"dynamic.terra.landed_cost.get_doctype_info",
           async: false,
           args:{
            doc_type : doctype ,
            document : doc_ument
           },
           callback:function (r){
              if (r.message){
                local.total =  r.message.total
                local.allocated_amount = r.message.allocated
                local.unallocated_amount = 0
                frm.refresh_field("cost_child_table")
                frm.events.set_applicabel_charges(frm)
              }
           }
       })
    } ,
    cost_child_table_remove:function(frm , cdt,cdn){
        
        frm.events.set_applicabel_charges(frm)
        if (frm.doc.cost_child_table.length > 0 ){
            frm.doc.cost_child_table.forEach(element=> {
                element.allocated_amount = element.allocated_amount + element.unallocated_amount
                element.unallocated_amount = 0 
            })
            frm.refresh_field("cost_child_table")
        }
        frappe.msgprint("Applicable Charges Will Updated For Invocie Allocated Amount Please Chek the Amount ")
    }

    


})