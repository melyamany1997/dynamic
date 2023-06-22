frappe.listview_settings['Attendance Rule'] = {
    onload: function(listview) {
        frappe.set_route("../../rules")
        window.location.reload()
        
    }


}