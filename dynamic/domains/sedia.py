from __future__ import unicode_literals
import frappe
data = {

    'custom_fields': {
        'Sales Invoice Item':[
            {
                "label":"Serial No Link",
                "fieldname":"serial_no_link",
                "fieldtype":"Link",
                "options":'Serial No',
                "insert_after":"serial_no",
            },
        ],
        
    },
      "properties": [

    ],
  
     'on_setup': 'dynamic.domains.sedia.create_sales_invoice_script'
}

def create_sales_invoice_script():
    name = "Sales Invoice-Form"
    if frappe.db.exists("Client Script",name) :
        doc = frappe.get_doc("Client Script",name)
    else :
        doc = frappe.new_doc("Client Script")
        doc.dt      = "Sales Invoice"
        doc.view    = "Form"
        doc.enabled = 1
    doc.script = r"""   

           

        frappe.ui.form.on("Sales Invoice",{
        refresh:(frm)=>{
            frm.set_query("serial_no_link", "items", function(doc, cdt, cdn) {
                var row = locals[cdt][cdn]
                        return {
                    filters: [
                    ["Serial No","item_code", "=", row.item_code]
                    ]
                }
        })
        }
    })
    frappe.ui.form.on('Sales Invoice Item', {
        serial_no_link:(frm,cdt,cdn)=>{
            var row = locals[cdt][cdn]
            if (!row.serial_no){
                row.serial_no = row.serial_no_link
            }
            else{
                row.serial_no += '\n'+row.serial_no_link 
            }
            
            
            
            frm.refresh_field("items")
        }
        
    })
        
        """
    doc.save()