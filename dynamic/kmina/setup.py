import frappe


def setup_kmina():
    create_sales_order_script()



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
        frappe.ui.form.on('Sales Order Item', {
            item_code:(frm,cdt,cdn)=>{
                 var row = locals[cdt][cdn];
                if (frm.doc.customer != "" && row.item_code){
                    frappe.call({
                        method:"dynamic.kmina.api.get_customer_item_code",
                        args:{
                            "customer": frm.doc.customer,
                            "item_code": row.item_code
                        },callback(r){
                            if(r.message){
                                let data = r.message
                                console.log("data",data)
                                if (data.length > 0){
                                    row.sfda_registration_no = data[0].sfda_registration_no
                                    row.hs_code = data[0].ref_code
                                    frm.refresh_field("items")
                                }
                            }
                        }
                    })
                }
            }
        })
        """
    doc.save()
