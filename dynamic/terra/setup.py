import frappe
from dynamic.dynamic_accounts.setup import add_properties_journal_auto


# DOMAINS = frappe.get_active_domains()



def create_workflow_status():
    if not frappe.db.exists("Workflow State","Submited"):
        submited_doc = frappe.new_doc("Workflow State")
        submited_doc.workflow_state_name = "Submited"
        submited_doc.save()
    if not frappe.db.exists("Workflow State","Approvd pending"):
        doc = frappe.new_doc("Workflow State")
        doc.workflow_state_name = "Approvd pending"
        doc.save()

def create_sales_order_work_flow():
    if not frappe.db.exists("Workflow","Sales Order Approval"):
        doc = frappe.new_doc("Workflow")
        doc.workflow_name = "Sales Order Approval"
        doc.document_type = "Sales Order"
        doc.is_active=1
        doc.append("states",{
            "state":"Approvd pending",
            "doc_status":0,
            "allow_edit":"Sales Manager"
        })
        doc.append("states",{
            "state":"Rejected",
            "doc_status":0,
            "allow_edit":"Sales Manager"
        })
        doc.append("states",{
            "state":"Rejected",
            "doc_status":0,
            "allow_edit":"Sales Manager"
        })
        doc.append("states",{
            "state":"Submited",
            "doc_status":1,
            "allow_edit":"Sales Manager"
        })

        doc.append("transitions",{
                "state":"Approvd pending",
                "action":"Approve",
                "next_state":"Submited",
                "allowed":"Sales Manager"
        })
        doc.append("transitions",{
                "state":"Approvd pending",
                "action":"Reject",
                "next_state":"Rejected",
                "allowed":"Sales Manager"
        })
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
            refresh(frm){
                console.log("refresh functions s s s s ")
                if(frm.doc.__islocal && frm.doc.is_return == 1){
                    frm.events.update_return_account(frm)
                }
            },
            is_return(frm){
                console.log("from return   asd ")
                if(frm.doc.__islocal && frm.doc.is_return == 1){
                    frm.events.update_return_account(frm)
                }
            },
            update_return_account(frm){
                frappe.call({
                        method:'dynamic.api.get_sales_return_account',
                        callback(r){
                            console.log("message =============> ",r.message)
                            if(r.message){
                                for(let i=0;i<frm.doc.items.length;i++){
                                    frm.doc.items[i].income_account = r.message
                                }    
                            }
                        }
                    })
                    frm.refresh_fields('items')
            }
        
        });


    """
    doc.save()



def create_item_script():
    name = "Item-Form"
    if frappe.db.exists("Client Script",name) :
        doc = frappe.get_doc("Client Script",name)
    else :
        doc = frappe.new_doc("Client Script")
        doc.dt      = "Item"
        doc.view    = "Form"
        doc.enabled = 1
    doc.script = """
            
        frappe.ui.form.on("Item", {
            item_group(frm){
                if(frm.doc.item_group && frm.doc.__islocal){
                    frappe.call({
                        method:'dynamic.api.generate_item_code',
                        args:{
                            'item_group':frm.doc.item_group
                        },callback(r){
                            if(r.message){
                                if(r.message == 'false'){
                                    frm.set_value("item_group","")
                                    frm.refresh_field('item_group')
                                }else{
                                frm.set_value('item_code',r.message)
                                frm.refresh_field('item_code')
                                }
                            }
                        }
                    })
                }
            }
        
        });
            frappe.ui.form.on('UOM Conversion Detail', {
            is_sub_uom:(frm,cdt,cdn)=>{
                var row = locals[cdt][cdn];
                var count_check = 0;
                for(let i =0;i<frm.doc.uoms.length;i++){
                    if(frm.doc.uoms[i].is_sub_uom==1){
                        count_check = count_check +1;
                    }
                }
                if(count_check >1){
                    row.is_sub_uom = 0
                    frm.refresh_fields("uoms")
                    frappe.throw(__("only one sub unit allowed"))
                }
                if (row.uom == frm.doc.stock_uom){
                    row.is_sub_uom = 0;
                    frm.refresh_fields("uoms")
                    frappe.throw(__("Sub UOM cant be eaqul default uom"))

                }
            }
        });


    """
    doc.save()


def create_delivery_note_script():
    name = "Delivery Note-Form"
    if frappe.db.exists("Client Script",name) :
        doc = frappe.get_doc("Client Script",name)
    else :
        doc = frappe.new_doc("Client Script")
        doc.dt      = "Delivery Note"
        doc.view    = "Form"
        doc.enabled = 1
    doc.script = """
            frappe.ui.form.on('Delivery Note Item', {
                qty:(frm,cdt,cdn)=>{
                    var row = locals[cdt][cdn];
                    frappe.call({
                        method:"dynamic.terra.api.get_iem_sub_uom",
                        args:{
                            "item_code":row.item_code,
                            "uom":row.uom,
                            "qty":row.qty
                        },callback(r){
                        console.log(r.message)
                            if(r.message){
                                let result = r.message
                                row.sub_uom = result.sub_uom;
                                row.sub_uom_conversation_factor = result.sub_uom_conversation_factor;
                                row.qty_as_per_sub_uom = result.qty_as_per_sub_uom;
                                frm.refresh_fields("items")
                            }
                        }
                    })
                },
                uom:(frm,cdt,cdn)=>{
                    var row = locals[cdt][cdn];
                    frappe.call({
                        method:"dynamic.terra.api.get_iem_sub_uom",
                        args:{
                            "item_code":row.item_code,
                            "uom":row.uom,
                            "qty":row.qty
                        },callback(r){
                        console.log(r.message)
                            if(r.message){
                                let result = r.message
                                row.sub_uom = result.sub_uom;
                                row.sub_uom_conversation_factor = result.sub_uom_conversation_factor;
                                row.qty_as_per_sub_uom = result.qty_as_per_sub_uom;
                                frm.refresh_fields("items")
                            }
                        }
                    })
                },
            
        })
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
            frappe.ui.form.on('Purchase Receipt Item', {
                qty:(frm,cdt,cdn)=>{
                    var row = locals[cdt][cdn];
                    frappe.call({
                        method:"dynamic.terra.api.get_iem_sub_uom",
                        args:{
                            "item_code":row.item_code,
                            "uom":row.uom,
                            "qty":row.qty + row.rejected_qty
                        },callback(r){
                        console.log(r.message)
                            if(r.message){
                                let result = r.message
                                row.sub_uom = result.sub_uom;
                                row.sub_uom_conversation_factor = result.sub_uom_conversation_factor;
                                row.qty_as_per_sub_uom = result.qty_as_per_sub_uom;
                                frm.refresh_fields("items")
                            }
                        }
                    })
                },
                rejected_qty:(frm,cdt,cdn)=>{
                    var row = locals[cdt][cdn];
                    frappe.call({
                        method:"dynamic.terra.api.get_iem_sub_uom",
                        args:{
                            "item_code":row.item_code,
                            "uom":row.uom,
                            "qty":row.qty + row.rejected_qty
                        },callback(r){
                        console.log(r.message)
                            if(r.message){
                                let result = r.message
                                row.sub_uom = result.sub_uom;
                                row.sub_uom_conversation_factor = result.sub_uom_conversation_factor;
                                row.qty_as_per_sub_uom = result.qty_as_per_sub_uom;
                                frm.refresh_fields("items")
                            }
                        }
                    })
                },
                uom:(frm,cdt,cdn)=>{
                    var row = locals[cdt][cdn];
                    frappe.call({
                        method:"dynamic.terra.api.get_iem_sub_uom",
                        args:{
                            "item_code":row.item_code,
                            "uom":row.uom,
                            "qty":row.qty
                        },callback(r){
                        console.log(r.message)
                            if(r.message){
                                let result = r.message
                                row.sub_uom = result.sub_uom;
                                row.sub_uom_conversation_factor = result.sub_uom_conversation_factor;
                                row.qty_as_per_sub_uom = result.qty_as_per_sub_uom;
                                frm.refresh_fields("items")
                            }
                        }
                    })
                },
            
        })
    """
    doc.save()

def create_lead_script():
    name = "Lead-Form"
    if frappe.db.exists("Client Script",name) :
        doc = frappe.get_doc("Client Script",name)
    else :
        doc = frappe.new_doc("Client Script")
        doc.dt      = "Lead"
        doc.view    = "Form"
        doc.enabled = 1
    doc.script = """
            
        frappe.ui.form.on("Lead", {
            refresh(frm){
                if(!frm.doc.__islocal){
                   frm.add_custom_button(
                __("New Appointment"),
                function () {
                  frappe.model.open_mapped_doc({
                    method:"dynamic.api.create_new_appointment",
                    frm: frm
                  });
                },
                __("Create")
              );
              frm.add_custom_button(
                __("Show History"),
                function () {
                  frappe.set_route('query-report','Actions Report',{"phone_no":frm.doc.phone_no})
                }
              );
                }
            }
        
        });


    """
    doc.save()

def create_customer_script():
    name = "Customer-Form"
    if frappe.db.exists("Client Script",name) :
        doc = frappe.get_doc("Client Script",name)
    else :
        doc = frappe.new_doc("Client Script")
        doc.dt      = "Customer"
        doc.view    = "Form"
        doc.enabled = 1
    doc.script = """
            
        frappe.ui.form.on("Customer", {
            refresh(frm){
                if(!frm.doc.__islocal){
              frm.add_custom_button(
                __("Show History"),
                function () {
                  frappe.set_route('query-report','Actions Report',{"phone_no":frm.doc.phone_no})
                }
              );
                }
            }
        
        });


    """
    doc.save()

def create_opportunity_script():
    name = "Opportunity-Form"
    if frappe.db.exists("Client Script",name) :
        doc = frappe.get_doc("Client Script",name)
    else :
        doc = frappe.new_doc("Client Script")
        doc.dt      = "Opportunity"
        doc.view    = "Form"
        doc.enabled = 1
    doc.script = """
            
        
            
        frappe.ui.form.on("Opportunity", {
            refresh(frm){
                if(!frm.doc.__islocal){
              frm.add_custom_button(
                __("Show History"),
                function () {
                  frappe.set_route('query-report','Actions Report',{"phone_no":frm.doc.phone_no})
                }
              );
                }
                if(!frm.doc.__islocal){
                frm.add_custom_button(__('Make Sales Order'),
                function() {
                	frm.trigger("make_sales_order")
                }, __('Create'));
                
                frm.add_custom_button(__('Make Material Request'),
                function() {
                	frm.trigger("make_material_request")
                }, __('Create'));
                }
            },
            make_sales_order:function(frm){
                frappe.model.open_mapped_doc({
                    method:"dynamic.terra.api.create_sales_order_from_opportunity",
                    frm:frm
                })
            },
            make_material_request:function(frm){
                frappe.model.open_mapped_doc({
                    method:"dynamic.terra.api.create_material_request_from_opportunity",
                    frm:frm
                })
            }
            
        
        });


    


    """
    doc.save()


def create_quotation_script():
    name = "Quotation-Form"
    if frappe.db.exists("Client Script",name) :
        doc = frappe.get_doc("Client Script",name)
    else :
        doc = frappe.new_doc("Client Script")
        doc.dt      = "Quotation"
        doc.view    = "Form"
        doc.enabled = 1
    doc.script = """
            frappe.ui.form.on('Quotation Item', {
            qty:(frm,cdt,cdn)=>{
                var row = locals[cdt][cdn];
                frappe.call({
                    method:"dynamic.terra.api.get_iem_sub_uom",
                    args:{
                        "item_code":row.item_code,
                        "uom":row.uom,
                        "qty":row.qty
                    },callback(r){
                    console.log(r.message)
                        if(r.message){
                            let result = r.message
                            row.sub_uom = result.sub_uom;
                            row.sub_uom_conversation_factor = result.sub_uom_conversation_factor;
                            row.qty_as_per_sub_uom = result.qty_as_per_sub_uom;
                            frm.refresh_fields("items")
                        }
                    }
                })
            },
            uom:(frm,cdt,cdn)=>{
                var row = locals[cdt][cdn];
                frappe.call({
                    method:"dynamic.terra.api.get_iem_sub_uom",
                    args:{
                        "item_code":row.item_code,
                        "uom":row.uom,
                        "qty":row.qty
                    },callback(r){
                    console.log(r.message)
                        if(r.message){
                            let result = r.message
                            row.sub_uom = result.sub_uom;
                            row.sub_uom_conversation_factor = result.sub_uom_conversation_factor;
                            row.qty_as_per_sub_uom = result.qty_as_per_sub_uom;
                            frm.refresh_fields("items")
                        }
                    }
                })
            },
            
        })
    """
    doc.save()



def create_sales_order_scipt():
    name = "Sales Order-Form"
    if frappe.db.exists("Client Script",name) :
        doc = frappe.get_doc("Client Script",name)
    else :
        doc = frappe.new_doc("Client Script")
        doc.dt      = "Sales Order"
        doc.view    = "Form"
        doc.enabled = 1
    doc.script = """
            
            frappe.ui.form.on('Sales Order',{
                setup: function (frm) {
                    frm.custom_make_buttons = {
                        "Sales Order Approval": "Sales Order Approval",
                    };
                },
               refresh:(frm)=>{
                    if(frm.doc.docstatus==1 && frm.doc.status == "To Deliver and Bill"){
                        frm.add_custom_button(
                    __("Sales Order Approval"),
                    function () {
                        frappe.model.open_mapped_doc({
        			method: "dynamic.terra.doctype.sales_order_approval.sales_order_approval.make_sales_order_approval",
        			frm: frm
        		})
                    },
                    __("Create")
                );
                }} 
            });
            frappe.ui.form.on('Sales Order Item', {
                qty:(frm,cdt,cdn)=>{
                    var row = locals[cdt][cdn];
                    frappe.call({
                        method:"dynamic.terra.api.get_iem_sub_uom",
                        args:{
                            "item_code":row.item_code,
                            "uom":row.uom,
                            "qty":row.qty
                        },callback(r){
                        console.log(r.message)
                            if(r.message){
                                let result = r.message
                                row.sub_uom = result.sub_uom;
                                row.sub_uom_conversation_factor = result.sub_uom_conversation_factor;
                                row.qty_as_per_sub_uom = result.qty_as_per_sub_uom;
                                frm.refresh_fields("items")
                            }
                        }
                    })
                },
                uom:(frm,cdt,cdn)=>{
                    var row = locals[cdt][cdn];
                    frappe.call({
                        method:"dynamic.terra.api.get_iem_sub_uom",
                        args:{
                            "item_code":row.item_code,
                            "uom":row.uom,
                            "qty":row.qty
                        },callback(r){
                        console.log(r.message)
                            if(r.message){
                                let result = r.message
                                row.sub_uom = result.sub_uom;
                                row.sub_uom_conversation_factor = result.sub_uom_conversation_factor;
                                row.qty_as_per_sub_uom = result.qty_as_per_sub_uom;
                                frm.refresh_fields("items")
                            }
                        }
                    })
                },
            
        })
    """
    doc.save()


def create_purchase_order_scipt():
    name = "Purchase Order-Form"
    if frappe.db.exists("Client Script",name) :
        doc = frappe.get_doc("Client Script",name)
    else :
        doc = frappe.new_doc("Client Script")
        doc.dt      = "Purchase Order"
        doc.view    = "Form"
        doc.enabled = 1
    doc.script = """
            frappe.ui.form.on('Purchase Order Item', {
                qty:(frm,cdt,cdn)=>{
                    var row = locals[cdt][cdn];
                    frappe.call({
                        method:"dynamic.terra.api.get_iem_sub_uom",
                        args:{
                            "item_code":row.item_code,
                            "uom":row.uom,
                            "qty":row.qty
                        },callback(r){
                        console.log(r.message)
                            if(r.message){
                                let result = r.message
                                row.sub_uom = result.sub_uom;
                                row.sub_uom_conversation_factor = result.sub_uom_conversation_factor;
                                row.qty_as_per_sub_uom = result.qty_as_per_sub_uom;
                                frm.refresh_fields("items")
                            }
                        }
                    })
                },
                uom:(frm,cdt,cdn)=>{
                    var row = locals[cdt][cdn];
                    frappe.call({
                        method:"dynamic.terra.api.get_iem_sub_uom",
                        args:{
                            "item_code":row.item_code,
                            "uom":row.uom,
                            "qty":row.qty
                        },callback(r){
                        console.log(r.message)
                            if(r.message){
                                let result = r.message
                                row.sub_uom = result.sub_uom;
                                row.sub_uom_conversation_factor = result.sub_uom_conversation_factor;
                                row.qty_as_per_sub_uom = result.qty_as_per_sub_uom;
                                frm.refresh_fields("items")
                            }
                        }
                    })
                },
            
        })
    """
    doc.save()


def create_stock_entry_scipt():
    name = "Stock Entry-Form"
    if frappe.db.exists("Client Script",name) :
        doc = frappe.get_doc("Client Script",name)
    else :
        doc = frappe.new_doc("Client Script")
    doc.dt      = "Stock Entry"
    doc.view    = "Form"
    doc.enabled = 1
    doc.script = """
            frappe.ui.form.on('Stock Entry Detail', {
                qty:(frm,cdt,cdn)=>{
                    var row = locals[cdt][cdn];
                    frappe.call({
                        method:"dynamic.terra.api.get_iem_sub_uom",
                        args:{
                            "item_code":row.item_code,
                            "uom":row.uom,
                            "qty":row.qty
                        },callback(r){
                        console.log(r.message)
                            if(r.message){
                                let result = r.message
                                row.sub_uom = result.sub_uom;
                                row.sub_uom_conversation_factor = result.sub_uom_conversation_factor;
                                row.qty_as_per_sub_uom = result.qty_as_per_sub_uom;
                                frm.refresh_fields("items")
                            }
                        }
                    })
                },
                uom:(frm,cdt,cdn)=>{
                    var row = locals[cdt][cdn];
                    frappe.call({
                        method:"dynamic.terra.api.get_iem_sub_uom",
                        args:{
                            "item_code":row.item_code,
                            "uom":row.uom,
                            "qty":row.qty
                        },callback(r){
                        console.log(r.message)
                            if(r.message){
                                let result = r.message
                                row.sub_uom = result.sub_uom;
                                row.sub_uom_conversation_factor = result.sub_uom_conversation_factor;
                                row.qty_as_per_sub_uom = result.qty_as_per_sub_uom;
                                frm.refresh_fields("items")
                            }
                        }
                    })
                },
            
        })
    """
    doc.save()

def create_material_request_script():
    name = "Material Request-Form"
    if frappe.db.exists("Client Script",name) :
        doc = frappe.get_doc("Client Script",name)
    else :
        doc = frappe.new_doc("Client Script")
    doc.dt      = "Material Request"
    doc.view    = "Form"
    doc.enabled = 1
    doc.script = """    
                frappe.ui.form.on('Material Request', {
                refresh:(frm)=>{
                    frm.add_custom_button(__('Quotation'), () => frm.events.get_items_from_quotation(frm),
                    __("Get Items From"));
                },
                get_items_from_quotation:(frm)=>{
                    console.log("quotation =======>",frm.doc.quotation)
                    if(frm.doc.quotation == undefined){
                        frappe.throw(__("You must choose quotation"))
                    }
                    frappe.call({
                        method:"dynamic.terra.api.get_quotation_item",
                        args:{
                            "quotation":frm.doc.quotation
                        },callback(r){
                            if(r.message){
                                let items = r.message;
                                for(let i=0;i<items.length;i++){
                                    var row = frm.add_child("items");
                                    row.item_code = items[i].item_code;
                                    row.item_name = items[i].item_name;
                                    row.qty = items[i].qty;
                                    row.rate = items[i].rate;
                                    row.description = items[i].description;
                                    row.uom = items[i].uom;
                                    row.schedule_date = items[i].schedule_date;
                                    row.stock_uom = items[i].stock_uom;
                                }
                                frm.refresh_fields("items");
                            }
                        }
                    })
                }
            })
        
        """
    doc.save()

def create_mode_of_payment_script():
    name = "Mode of Payment-Form"
    if frappe.db.exists("Client Script",name) :
        doc = frappe.get_doc("Client Script",name)
    else :
        doc = frappe.new_doc("Client Script")
        doc.dt      = "Mode of Payment"
        doc.view    = "Form"
        doc.enabled = 1
    doc.script = """   
                   
                
                frappe.ui.form.on('Mode of Payment', {
                        refresh:(frm)=>{
                    frm.set_query("recived_account", function () {
                    return {
                        filters: [
                        ["is_group", "=", 0]
                        ],
                    };
                    });
                    frm.set_query("cost_center", function () {
                    return {
                        filters: [
                        ["is_group", "=", 0]
                        ],
                    };
                    });
                
            }
            });
         
        """
    doc.save()

def create_payment_entry_script():
    name = "Payment Entry-Form"
    if frappe.db.exists("Client Script",name) :
        doc = frappe.get_doc("Client Script",name)
    else :
        doc = frappe.new_doc("Client Script")
        doc.dt      = "Payment Entry"
        doc.view    = "Form"
        doc.enabled = 1
    doc.script = """   
                   
                frappe.ui.form.on('Payment Entry', {
                paid_amount:(frm)=>{
                    frm.events.get_deduct_amount(frm);
                },
                mode_of_payment:(frm)=>{
                    if(frm.doc.mode_of_payment !=''){
                        frm.events.get_deduct_amount(frm);
                        frappe.call({
                        "method":"dynamic.api.validate_mode_of_payment_naming",
                        args:{
                            old_naming:frm.doc.mode_of_payment_naming,
                            mode_of_payment:frm.doc.mode_of_payment
                        },callback(r){
                            if(!r.message){
                                frm.set_value("mode_of_payment",'');
                                frappe.throw(__("Different naming template"))
                            }
                        }
                    })
                    }
                    
                },
                get_deduct_amount:(frm)=>{
                    cur_frm.clear_table("taxes");
                    frm.refresh_fields("taxes");
                    frappe.call({
                        "method": "frappe.client.get",
                            args: {
                                doctype: "Mode of Payment",
                                name: frm.doc.mode_of_payment
                            },callback(r){
                                if(r.message){
                                    let res = r.message;
                                    if(res.has_deduct){
                                        var row = cur_frm.add_child("taxes")
                                        row.charge_type = "Actual";
                                        row.account_head = res.recived_account;
                                        row.description = res.recived_account;
                                        // row.percentage = res.deduct_percentage;
                                        //row.cost_center = res.cost_center
                                        row.rate =res.deduct_percentage; //frm.doc.paid_amount * (res.deduct_percentage/100);
                                        row.tax_amount = frm.doc.paid_amount * (res.deduct_percentage/100);
                                        frm.refresh_fields("taxes");
                                    }
                                }
                            }
                    })
                }
            })
        
        
        
        """
    doc.save()
# def create_item_script():
#     name = "Item-Form"
#     if frappe.db.exists("Client Script",name) :
#         doc = frappe.get_doc("Client Script",name)
#     else :
#         doc = frappe.new_doc("Client Script")
#     doc.dt      = "Stock Entry"
#     doc.view    = "Form"
#     doc.enabled = 1
#     doc.script = """
#             frappe.ui.form.on('Item', {
#                 qty:(frm,cdt,cdn)=>{
#                     var row = locals[cdt][cdn];
#                     frappe.call({
#                         method:"dynamic.terra.api.get_iem_sub_uom",
#                         args:{
#                             "item_code":row.item_code,
#                             "uom":row.uom,
#                             "qty":row.qty
#                         },callback(r){
#                         console.log(r.message)
#                             if(r.message){
#                                 let result = r.message
#                                 row.sub_uom = result.sub_uom;
#                                 row.sub_uom_conversation_factor = result.sub_uom_conversation_factor;
#                                 row.qty_as_per_sub_uom = result.qty_as_per_sub_uom;
#                                 frm.refresh_fields("items")
#                             }
#                         }
#                     })
#                 }
            
#         })
#     """
#     doc.save()



def add_property_setters():
    name = "Item-item_code-read_only"
    if frappe.db.exists("Property Setter",name) :
        pass
    else:
        doc = frappe.new_doc("Property Setter")
        doc.doctype_or_field="DocField"
        doc.doc_type="Item"
        doc.field_name="item_code"
        doc.property="read_only"
        doc.property_type="Check"
        doc.value=1
        doc.save()

def add_lead_property_setters():
    name = "Lead-main-search_fields"
    if frappe.db.exists("Property Setter",name) :
        pass
    else:
        doc = frappe.new_doc("Property Setter")
        doc.doctype_or_field="DocType"
        doc.doc_type="Lead"
        doc.property="search_fields"
        doc.property_type="Data"
        doc.value="lead_name,lead_owner,status,phone_no"
        doc.save()

def add_opp_property_setters():
    name = "Opportunity-main-search_fields"
    if frappe.db.exists("Property Setter",name) :
        pass
    else:
        doc = frappe.new_doc("Property Setter")
        doc.doctype_or_field = "DocType"
        doc.doc_type = "Opportunity"
        doc.property = "search_fields"
        doc.property_type = "Data"
        doc.value="status,transaction_date,party_name,opportunity_type,territory,company,phone_no"
        doc.save()

def add_customer_property_setters():
    name = "Customer-main-search_fields"
    if frappe.db.exists("Property Setter",name) :
        pass
    else:
        doc = frappe.new_doc("Property Setter")
        doc.doctype_or_field="DocType"
        doc.doc_type="Customer"
        doc.property="search_fields"
        doc.property_type="Data"
        doc.value="customer_name,customer_group,territory, mobile_no,primary_address,phone_no"
        doc.save()




def install_action():
    data =[
            {
            "type": "Indoor",
            "action_name": "Visit"
            },
            {
                "type": "Indoor",
                "action_name": "Call"
            },
            {
                "type": "Out door",
                "action_name": "Out"
            }

        ]
    for i in data :
        if not frappe.db.exists("Action",i.get("action_name")) :
            frappe.get_doc({
                "doctype":"Action",
                "type":i.get("type"),
                "action_name":i.get("action_name")
            }).insert()
# Create two Stock Entry Types --  Material Send -- Matrial Receive
def create_trans():
    name ="Transfer"
    # if exit 
    exit_name= frappe.db.sql(f""" 
    SELECT name FROM `tabStock Entry Type` WHERE name = '{name}'
    """,as_dict=1)
    if not exit_name or len(exit_name) == 0 :
        #create Stock Entry Type 
        new_type = frappe.new_doc("Stock Entry Type")
        new_type.__newname = name
        new_type.purpose = "Material Transfer"
        new_type.add_to_transit = 1
        new_type.save()




def create_terra_scripts():
    create_trans()
    try:
        create_sales_invoice_script()
        add_properties_journal_auto()
    except:
        print("error in create sales order script")

    
    try:
        create_item_script()
    except:
        print("error in create_item_script")

    try: 
        create_lead_script()
    except:
        pass
    
    try:
        create_customer_script()
    except:
        pass
    
    try:
        create_opportunity_script()
    except:
        pass
    try:
        add_property_setters()
    except:
        print("error in add_property_setters")

    try:
        add_lead_property_setters()
    except:
        print("add_item_property_setters")

    try:
        add_opp_property_setters()
    except:
        print("add_opp_property_setters")

    try:
        add_customer_property_setters()
    except:
        print("add_customer_property_setters")
    try:
        create_quotation_script()
    except Exception as ex:
        print("error while create quotation script '%s'"%str(ex))
    try:
        create_sales_order_scipt()
    except Exception as ex:
        print("error while create sales order script '%s'"%str(ex))
    try:
        create_purchase_order_scipt()
    except:
        pass
    try:
        create_delivery_note_script()
    except Exception as ex:
        print("error on create delivery note script")
    try:
        create_stock_entry_scipt()
    except:
        print("error")

    try:
        create_purchase_recipt_script()
    except:
        pass
    try:
        create_material_request_script()
    except:
        pass
    try:
        create_payment_entry_script()
    except Exception as ex:
        pass
    try:
        install_action()
    except Exception as ex:
        print("----------------------- install_actioninstall_actioninstall_action",str(ex))
    try:
        create_mode_of_payment_script()
    except:
        pass
    # try:
    #     create_workflow_status()
    # except:
    #     pass 
    # try:
    #     create_sales_order_work_flow()
    # except:
    #     pass

    
    # create_workflow_status()
    # create_sales_order_work_flow()



