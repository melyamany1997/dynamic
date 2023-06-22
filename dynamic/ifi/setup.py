import frappe

Domains = frappe.get_active_domains()

def setup_ifi():
    create_ifi_scripts()
    # frappe.msgprint('created')

def create_ifi_scripts():
    try: 
        create_lead_script()
        create_customer_script()
        create_opportunity_script()
        install_action()
    except Exception as ex:
        pass

def create_lead_script():
    if 'Terra' not in Domains:
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
                        method:"dynamic.ifi.api.create_new_appointment_ifi",
                        frm: frm
                    });
                    },
                    __("Create")
                );
                frm.add_custom_button(
                    __("Action"),
                    function () {
                    frappe.model.open_mapped_doc({
                        method:"dynamic.ifi.api.create_action_lead",
                        frm: frm
                    });
                    },
                    __("Create")
                );
                
                    }
                }
            
            });
        """
        doc.save()

def create_customer_script():
    name = "Customer-Form"
    if not frappe.db.exists("Client Script",name) :
        doc = frappe.new_doc("Client Script")
        doc.dt      = "Customer"
        doc.view    = "Form"
        doc.enabled = 1
        doc.script = """ 
         frappe.ui.form.on("Customer", {
                refresh(frm){
                    if(!frm.doc.__islocal){
                    frm.add_custom_button(
                    __("Action"),
                    function () {
                    frappe.model.open_mapped_doc({
                        method:"dynamic.ifi.api.create_action_cst",
                        frm: frm
                    });
                    },
                    __("Create")
                );
                    }
                    }
            
            });
                
        """
        doc.save()

def create_opportunity_script():
    name = "Opportunity-Form"
    if not frappe.db.exists("Client Script",name) :
        doc = frappe.new_doc("Client Script")
        doc.dt      = "Opportunity"
        doc.view    = "Form"
        doc.enabled = 1
        doc.script = """ 
         frappe.ui.form.on("Opportunity", {
                refresh(frm){
                    if(!frm.doc.__islocal){
                    frm.add_custom_button(
                    __("Action"),
                    function () {
                    frappe.model.open_mapped_doc({
                        method:"dynamic.ifi.api.create_action_opportunity",
                        frm: frm
                    });
                    },
                    __("Create")
                );
                    }
                    }
            
            });
                
        """
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
        if not frappe.db.exists("Action",{"action_name":i.get("action_name")}) :
            frappe.get_doc({
                "doctype":"Action",
                "type":i.get("type"),
                "action_name":i.get("action_name")
            }).insert()

