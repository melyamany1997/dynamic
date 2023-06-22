import frappe 




def create_property_setter():
    if not frappe.db.exists("Property Setter","Batch-main-search_fields"):
        doc = frappe.new_doc("Property Setter")
        doc.doctype_or_field = "DocType"
        doc.doc_type = "Batch"
        doc.property = "search_fields"
        doc.property_type = "Data"
        doc.value = "barcode"
        doc.save()

def create_sales_invoice_script():
    name = "Sales Invoice-Form"
    if frappe.db.exists("Client Script",name) :
        doc = frappe.get_doc("Client Script",name)
    else :
        doc = frappe.new_doc("Client Script")
        doc.dt      = "Sales Invoice"
        doc.view    = "Form"
        doc.enabled = 1
    doc.script = """
            
        frappe.ui.form.on("Sales Invoice", {
            batch_barcode:(frm)=>{
                if(frm.doc.batch_barcode.length > 0){
                    frappe.call({
                        "method": "frappe.client.get",
                            args: {
                                doctype: "Batch",
                                name: frm.doc.batch_barcode
                            },callback(r){
                                if(r.message){
                                    let res = r.message;
                                    var row = cur_frm.add_child("items")
                                    row.item_code=res.item;
                                    row.batch_no=frm.doc.batch_barcode;
                                    row.uom=res.stock_uom;
                                    row.stock_uom=res.stock_uom;
                                    row.item_name = res.item_name;
                                    row.conversion_factor=1;
                                    row.qty=1;
                                    frappe.call({
                                        "method":"dynamic.api.get_item_price",
                                        args:{
                                          "item_code":res.item,
                                          "price_list":'Standard Selling'
                                        },
                                        callback(r){
                                            if(r.message){
                                                row.rate = r.message;
                                                row.amount = row.rate * row.qty;
                                            }
                                            frm.refresh_fields("items");
                                            frm.set_value("batch_barcode","");
                                        }
                                    })
                                    
                                }
                            }
                    })
                }
            }
        
        });
    """
    doc.save()


def create_sales_order_script():
    name = "Sales Order-Form"
    if frappe.db.exists("Client Script",name) :
        doc = frappe.get_doc("Client Script",name)
    else :
        doc = frappe.new_doc("Client Script")
        doc.dt      = "Sales Order"
        doc.view    = "Form"
        doc.enabled = 1
    doc.script = """
            
        frappe.ui.form.on("Sales Order", {
            batch_barcode:(frm)=>{
                if(frm.doc.batch_barcode.length > 0){
                    frappe.call({
                        "method": "frappe.client.get",
                            args: {
                                doctype: "Batch",
                                name: frm.doc.batch_barcode
                            },callback(r){
                                if(r.message){
                                    let res = r.message;
                                    var row = cur_frm.add_child("items")
                                    row.item_code=res.item;
                                    row.batch_no=frm.doc.batch_barcode;
                                    row.uom=res.stock_uom;
                                    row.stock_uom=res.stock_uom;
                                    row.item_name = res.item_name;
                                    row.conversion_factor=1;
                                    row.qty=1;
                                    frappe.call({
                                        "method":"dynamic.api.get_item_price",
                                        args:{
                                          "item_code":res.item,
                                          "price_list":'Standard Selling'
                                        },
                                        callback(r){
                                            if(r.message){
                                                row.rate = r.message;
                                                row.amount = row.rate * row.qty;
                                            }
                                            frm.refresh_fields("items");
                                            frm.set_value("batch_barcode","");
                                        }
                                    })
                                    
                                }
                            }
                    })
                }
            }
        
        });
    """
    doc.save() 

def create_purchase_recipt_script():
    name = "Purchase Receipt-Form"
    if frappe.db.exists("Client Script",name) :
        doc = frappe.get_doc("Client Script",name)
    else :
        doc = frappe.new_doc("Client Script")
        doc.dt      = "Purchase Receipt"
        doc.view    = "Form"
        doc.enabled = 1
    doc.script = """
            
        frappe.ui.form.on("Purchase Receipt", {
            batch_barcode:(frm)=>{
                if(frm.doc.batch_barcode.length > 0){
                    frappe.call({
                        "method": "frappe.client.get",
                            args: {
                                doctype: "Batch",
                                name: frm.doc.batch_barcode
                            },callback(r){
                                if(r.message){
                                    let res = r.message;
                                    var row = cur_frm.add_child("items")
                                    row.item_code=res.item;
                                    row.batch_no=frm.doc.batch_barcode;
                                    row.uom=res.stock_uom;
                                    row.stock_uom=res.stock_uom;
                                    row.item_name = res.item_name;
                                    row.conversion_factor=1;
                                    row.description = res.item_name;
                                    row.qty=1;
                                    frappe.call({
                                        "method":"dynamic.api.get_item_price",
                                        args:{
                                          "item_code":res.item,
                                          "price_list":'Standard Buying'
                                        },
                                        callback(r){
                                            if(r.message){
                                                row.rate = r.message;
                                                row.amount = row.rate * row.qty;
                                            }
                                            frm.refresh_fields("items");
                                            frm.set_value("batch_barcode","");
                                        }
                                    })
                                    
                                }
                            }
                    })
                }
            }
        
        });
    """
    doc.save()  

def create_purchase_invoice_script():
    name = "Purchase Invoice-Form"
    if frappe.db.exists("Client Script",name) :
        doc = frappe.get_doc("Client Script",name)
    else :
        doc = frappe.new_doc("Client Script")
        doc.dt      = "Purchase Invoice"
        doc.view    = "Form"
        doc.enabled = 1
    doc.script = """
            
        frappe.ui.form.on("Purchase Invoice", {
            batch_barcode:(frm)=>{
                if(frm.doc.batch_barcode.length > 0){
                    frappe.call({
                        "method": "frappe.client.get",
                            args: {
                                doctype: "Batch",
                                name: frm.doc.batch_barcode
                            },callback(r){
                                if(r.message){
                                    let res = r.message;
                                    var row = cur_frm.add_child("items")
                                    row.item_code=res.item;
                                    row.batch_no=frm.doc.batch_barcode;
                                    row.uom=res.stock_uom;
                                    row.stock_uom=res.stock_uom;
                                    row.item_name = res.item_name;
                                    row.conversion_factor=1;
                                    row.qty=1;
                                    frappe.call({
                                        "method":"dynamic.api.get_item_price",
                                        args:{
                                          "item_code":res.item,
                                          "price_list":'Standard Buying'
                                        },
                                        callback(r){
                                            if(r.message){
                                                row.rate = r.message;
                                                row.amount = row.rate * row.qty;
                                            }
                                            frm.refresh_fields("items");
                                            frm.set_value("batch_barcode","");
                                        }
                                    })
                                    
                                }
                            }
                    })
                }
            }
        
        });
    """
    doc.save()  

def create_purchase_invoice_script():
    name = "Purchase Order-Form"
    if frappe.db.exists("Client Script",name) :
        doc = frappe.get_doc("Client Script",name)
    else :
        doc = frappe.new_doc("Client Script")
        doc.dt      = "Purchase Order"
        doc.view    = "Form"
        doc.enabled = 1
    doc.script = """
            
        frappe.ui.form.on("Purchase Order", {
            batch_barcode:(frm)=>{
                if(frm.doc.batch_barcode.length > 0){
                    frappe.call({
                        "method": "frappe.client.get",
                            args: {
                                doctype: "Batch",
                                name: frm.doc.batch_barcode
                            },callback(r){
                                if(r.message){
                                    let res = r.message;
                                    var row = cur_frm.add_child("items")
                                    row.item_code=res.item;
                                    row.batch_no=frm.doc.batch_barcode;
                                    row.uom=res.stock_uom;
                                    row.stock_uom=res.stock_uom;
                                    row.item_name = res.item_name;
                                    row.conversion_factor=1;
                                    row.qty=1;
                                    frappe.call({
                                        "method":"dynamic.api.get_item_price",
                                        args:{
                                          "item_code":res.item,
                                          "price_list":'Standard Buying'
                                        },
                                        callback(r){
                                            if(r.message){
                                                row.rate = r.message;
                                                row.amount = row.rate * row.qty;
                                            }
                                            frm.refresh_fields("items");
                                            frm.set_value("batch_barcode","");
                                        }
                                    })
                                    
                                }
                            }
                    })
                }
            }
        
        });
    """
    doc.save()

def create_stock_entry_script():
    name = "Stock Entry-Form"
    if frappe.db.exists("Client Script",name) :
        doc = frappe.get_doc("Client Script",name)
    else :
        doc = frappe.new_doc("Client Script")
        doc.dt      = "Stock Entry"
        doc.view    = "Form"
        doc.enabled = 1
    doc.script = """
            
        frappe.ui.form.on("Stock Entry", {
            batch_barcode:(frm)=>{
                if(frm.doc.batch_barcode.length > 0){
                    frappe.call({
                        "method": "frappe.client.get",
                            args: {
                                doctype: "Batch",
                                name: frm.doc.batch_barcode
                            },callback(r){
                                if(r.message){
                                    let res = r.message;
                                    var row = cur_frm.add_child("items")
                                    row.item_code=res.item;
                                    row.batch_no=frm.doc.batch_barcode;
                                    row.uom=res.stock_uom;
                                    row.stock_uom=res.stock_uom;
                                    row.item_name = res.item_name;
                                    row.conversion_factor=1;
                                    row.qty=1;
                                    frappe.call({
                                        "method":"dynamic.api.get_item_price",
                                        args:{
                                          "item_code":res.item,
                                          "price_list":'Standard Buying'
                                        },
                                        callback(r){
                                            if(r.message){
                                                row.basic_rate = r.message;
                                                row.amount = row.basic_rate * row.qty;
                                            }
                                            frm.refresh_fields("items");
                                            frm.set_value("batch_barcode","");
                                        }
                                    })
                                    
                                }
                            }
                    })
                }
            }
        
        });
    """
    doc.save()  



def create_scripts():
    try:
        create_sales_invoice_script()
    except:
        pass

    try:
        create_sales_order_script()
    except:
        pass 

    try:
        create_purchase_invoice_script()
    except:
        pass 
    
    try:
        create_purchase_recipt_script()
    except:
        pass
    try:
        create_stock_entry_script()
    except:
        pass
    try:
        create_property_setter()
    except:
        pass