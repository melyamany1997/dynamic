
frappe.ui.form.on("Stock Entry", {

    // setup :function(frm){

    //   frappe.call({
    //       "method" : "dynamic.contracting.doctype.stock_functions.fetch_contracting_data" ,
    //       callback :function(r){
    //         console.log(r)
    //         if (r.message){

    //         }
    //       }
    //   })
       
    // },
    trea_setup(frm){
      frappe.call({
        method:"dynamic.api.validate_terra_domain",
        callback:function(r) {
          if (r.message){
            frm.events.terra_stock_etnrty(frm)
          }
        }
       })
  
    },
    terra_stock_etnrty(frm){
      console.log("tera")
      if (frm.doc.add_to_transit === 0){
      
          frm.remove_custom_button(__('End Transit')) 
        
        }
      if (frm.doc.__islocal && frm.doc.outgoing_stock_entry) {

        frappe.call({
          method: 'frappe.client.get_value',
          "args":{
            "doctype": 'Stock Entry',
            "fieldname": "ds_warehouse",
            "filters": {
              'name': frm.doc.outgoing_stock_entry,
            
            },
          },
          callback: function (data) {
             frm.set_value("to_warehouse" ,  data.message.ds_warehouse )
             frm.set_df_property("to_warehouse", 'read_only', 1);
             frm.refresh_field("to_warehouse")
          }

        })
       
        

      }
      
    },
    onload:function(frm) {
    //  add tarra customization 
    
     frm.events.trea_setup(frm)
     
    },
    refresh:function(frm){
      frm.events.trea_setup(frm)
      frm.events.set_property(frm)
    },
    add_to_transit : function (frm) {
      frm.events.set_property(frm)
    },
    set_property(frm){
      var ds_warehouse_reqrd = (frm.doc.add_to_transit == 1) ? 1:0
      frm.set_df_property("ds_warehouse", "reqd", ds_warehouse_reqrd )
      frm.refresh_field("ds_warehouse")
    },
    comparison : function (frm) {
        if(frm.doc.against_comparison){

          frappe.call({
            "method" : "dynamic.contracting.doctype.stock_functions.stock_entry_setup" ,
            args:{
              "comparison" : frm.doc.comparison
            },
            callback :function(r){
              if (r.message){

                frm.set_query("comparison_item",function () {
                  return {
                    filters: [
                      ["item_code", "in", r.message],
                     
                    ],
                  };
                });
                frm.refresh_field("comparison_item")
                frm.set_query("comparison_item","items",function () {
                  return {
                    filters: [
                      ["item_code", "in", r.message],
                     
                    ],
                  };
                });
                frm.refresh_field("items")

              }
            } 
         
          })
       
        
        
      
      }
    },
    cost_center:function(frm){
      if(frm.doc.cost_center){
        frappe.call({
          method: "dynamic.api.get_active_domains",
          callback: function (r) {
              if (r.message && r.message.length) {
                  if (r.message.includes("Maser2000")) {
                    $.each(frm.doc.items || [], function(i, d) {
                      d.cost_center = frm.doc.cost_center;
                    });
                    refresh_field("items");
                  }
              }
          }
      })
      }
    }


})

