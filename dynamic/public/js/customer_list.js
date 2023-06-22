frappe.listview_settings['Customer'] = {

    
    onload: function(listview) {
        
        var validate_domain = "dynamic.api.validate_whats_app_settings" 
     
        listview.page.add_menu_item(__("Send WhatsApp Message"), function() {
            var data = 	listview.get_checked_items()
             frappe.call({
                method:validate_domain ,
                args :
                {"data" : data}

             })
        
             

        })
        
    }
    
}