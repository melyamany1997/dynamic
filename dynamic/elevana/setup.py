import frappe


def install_elevana():
    create_item_script()
    create_sales_order_script()

def create_item_script():
    name = "Item-Form"
    if frappe.db.exists("Client Script", name):
        doc = frappe.get_doc("Client Script", name)
    else:
        doc = frappe.new_doc("Client Script")
        doc.dt = "Item"
        doc.view = "Form"
        doc.enabled = 1
    doc.script = """   
        frappe.ui.form.on('Item', {
            refresh(frm){
                frm.add_custom_button(__("Create item in Shipping"), function() {
                frappe.call({
                method:"dynamic.shipping.api.create_product",
                args:{
                    "product" : frm.doc
                },callback(r){
                    if(r.message){
                        frappe.msgprint(r.message)
                    }
                }
                })
        })
            }
        })
        """
    doc.save()


def create_sales_order_script():
    name = "Sales Order-Form"
    if frappe.db.exists("Client Script", name):
        doc = frappe.get_doc("Client Script", name)
    else:
        doc = frappe.new_doc("Client Script")
        doc.dt = "Sales Order"
        doc.view = "Form"
        doc.enabled = 1
    doc.script = """   
            frappe.ui.form.on('Sales Order', {
                        refresh(frm){
                if(frm.doc.docstatus ==1 && frm.doc.is_synced == 0){
                frm.add_custom_button(__("flextock"), function() {
                frappe.call({
                method:"dynamic.shipping.api.create_order",
                args:{
                    "doc" : frm.doc
                },callback(r){
                    if(r.message){
                        frappe.msgprint(r.message)
                    }
                }
                })
        },"Shipping With") 
        
        frm.add_custom_button(__("j & t"), function() {
                frappe.call({
                method:"dynamic.shipping.jandt.create_oder",
                args:{
                    "product" : frm.doc
                },callback(r){
                    if(r.message){
                        frappe.msgprint(r.message)
                    }
                }
                })
        },"Shipping With")
         frm.add_custom_button(__("RTX"), function() {
                frappe.call({
                method:"dynamic.shipping.rtx.create_oder",
                args:{
                    "product" : frm.doc
                },callback(r){
                    if(r.message){
                        frappe.msgprint(r.message)
                    }
                }
                })
        },"Shipping With")
        
        
            }
            if(frm.doc.is_synced == 1 && frm.doc.shipping_company == "jandt"){
                frm.add_custom_button(__("Cancel Order Shipping"), function() {
                frappe.call({
                method:"dynamic.shipping.jandt.cancel_order",
                args:{
                    "order" : frm.doc
                },callback(r){
                    if(r.message){
                        frappe.msgprint(r.message)
                    }
                }
                })
        })
            }
            }
        })
        
        
        
        """
    doc.save()
