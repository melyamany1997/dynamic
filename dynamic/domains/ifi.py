

from __future__ import unicode_literals
installation_status = [
    "",
    "Pending",
    "Start",
    "Inprogress",
    "Completed",
]

data = {

    'custom_fields': {
        'Company':[
            {
                "label":"Crean Income Account",
                "fieldname":"crean_income_account",
                "fieldtype":"Link",
                "options":'Account',
                "insert_after":"monthly_sales_target"
            },
        ],
        'Sales Invoice':[
            {
                "label": "Crean",
                "fieldname": "crean",
                "fieldtype": "Select",
                "options":"\nYes\nNo",
                "insert_after": "customer",
                "reqd":1
            },
            {
                "label": "Crean Amount",
                "fieldname": "crean_amount",
                "fieldtype": "Float",
                "insert_after": "crean",
            },
        ],
        'Purchase Order':[
             {
                "fieldname": "customer_so",
                "fieldtype": "Link",
                "options":"Customer",
                "insert_after": "more_info",
                "label": "Customer SO",
                "in_standard_filter":1
            },
            {
                "label": "Delivery Date",
                "fieldname": "delivery_date",
                "fieldtype": "Date",
                "insert_after": "schedule_date",
                "in_standard_filter":1

            },
            {
                "fieldname": "crean",
                "fieldtype": "Select",
                "options":"\nYes\nNo",
                "insert_after": "apply_tds",
                "label": "Crean",
                "reqd":1
            },
            {
                "fieldname": "crean_amount",
                "fieldtype": "Float",
                "insert_after": "crean",
                "label": "Crean Amount",
            },

        ],
         'Quotation':[
            {
                "fieldname": "crean",
                "fieldtype": "Select",
                "options":"\nYes\nNo",
                "insert_after": "customer_name",
                "label": "Crean",
                "reqd":1
            },
            {
                "fieldname": "crean_amount",
                "fieldtype": "Float",
                "insert_after": "crean",
                "label": "Crean Amount",
            },
           
         ],
         'Opportunity':[
            {
                "label": "Opportunity Status",
                "fieldname": "oportunity_status",
                "fieldtype": "Link",
                "options":"Opportunity Status",
                "insert_after": "expected_closing",
            },
            {
                "label": "Campaign Name",
                "fieldname": "campaign_name",
                "fieldtype": "Link",
                "options":"Campaign",
                "insert_after": "source",
            },
         ],
         'Sales Order':[
            {
                "label": "Sales Installation",
                "fieldname": "sales_installation",
                "fieldtype": "Select",
                "options":"\n".join(installation_status),
                "default":"",
                "insert_after": "more_info",
                "read_only" : 1,
                "allow_on_submit": 1,
                "in_standard_filter":1,
                "in_list_view":1
            },
            {
                "label": "Crean",
                "fieldname": "crean",
                "fieldtype": "Select",
                "options":"\nYes\nNo",
                "insert_after": "order_type",
                "reqd":1
            },
            {
                "label": "Crean Amount",
                "fieldname": "crean_amount",
                "fieldtype": "Float",
                "insert_after": "crean",
            },
            {
                "label": "Advance Paymentstest",
                "fieldname": "advance_paymentss",
                "fieldtype": "Section Break",
                "insert_after": "payment_schedule"
            },
            {
                "label": "Get Advances Receivedd",
                "fieldname": "get_advancess",
                "fieldtype": "Button",
                "insert_after": "advance_paymentss",
                "allow_on_submit":1
            },
            {
                "label": "Advances",
                "fieldname": "advancess",
                "fieldtype": "Table",
                "options":"Sales Invoice Advance",
                "insert_after": "get_advancess",
                "allow_on_submit":1
            },
             {
                "label": "% Orderd",
                "fieldname": "per_orderd",
                "fieldtype": "Percent",
                "insert_after": "per_delivered",
                "allow_on_submit":1
            },
         ],
         'Lead':[
            {
            "label": "Phone No.",
            "fieldname": "phone_no1",
            "fieldtype": "Data",
            "insert_after": "contact_by",
            "unique":1,
            "reqd":1
            },
            {
                "label": "URL",
                "fieldname": "url",
                "fieldtype": "Small Text",
                "insert_after": "email_id",
                "allow_on_submit": 1    
            },
            {
                "label": "Check Url",
                "fieldname": "check_url",
                "fieldtype": "Button",
                "insert_after": "url",
            },
            
            
           
         ],
         'Customer':[
            {
                "label": "URL",
                "fieldname": "url",
                "fieldtype": "Small Text",
                "insert_after": "opportunity_name",
                "allow_on_submit": 1    
            },
            {
                "label": "Check Url",
                "fieldname": "check_url",
                "fieldtype": "Button",
                "insert_after": "url",
            },
         ],
         'Supplier':[
            {
                "label": "URL",
                "fieldname": "url",
                "fieldtype": "Small Text",
                "insert_after": "tax_withholding_category",
                "allow_on_submit": 1    
            },
            {
                "label": "Check Url",
                "fieldname": "check_url",
                "fieldtype": "Button",
                "insert_after": "url",
            },
         ],
         'Purchase Invoice':[
             {
                "fieldname": "crean",
                "fieldtype": "Select",
                "options":"\nYes\nNo",
                "insert_after": "due_date",
                "label": "Crean",
                "reqd":1
            },
            {
                "fieldname": "crean_amount",
                "fieldtype": "Float",
                "insert_after": "crean",
                "label": "Crean Amount",
            },
         ],
    },
      "properties": [
        {
        "doctype": "Quotation",
        "doctype_or_field": "DocField",
        "fieldname": "payment_schedule",
        "property": "allow_on_submit",
        "property_type": "Check",
        "value": "1"
        },
        {
        "doctype": "Sales Invoice",
        "doctype_or_field": "DocField",
        "fieldname": "taxes_and_charges",
        "property": "reqd",
        "property_type": "Check",
        "value": "1"
        },
        {
        "doctype": "Sales Order",
        "doctype_or_field": "DocField",
        "fieldname": "taxes_and_charges",
        "property": "reqd",
        "property_type": "Check",
        "value": "1"
        },
        {
        "doctype": "Purchase Order",
        "doctype_or_field": "DocField",
        "fieldname": "taxes_and_charges",
        "property": "reqd",
        "property_type": "Check",
        "value": "1"
        },
        {
        "doctype": "Purchase Invoice",
        "doctype_or_field": "DocField",
        "fieldname": "taxes_and_charges",
        "property": "reqd",
        "property_type": "Check",
        "value": "1"
        },
        {
        "doctype": "Quotation",
        "doctype_or_field": "DocField",
        "fieldname": "taxes_and_charges",
        "property": "reqd",
        "property_type": "Check",
        "value": "1"
        },
        {
        "doctype": "Sales Order",
        "doctype_or_field": "DocField",
        "fieldname": "order_type",
        "property": "options",
        "property_type": "Text",
        "value": "\nSales\nMaintenance\nShopping Cart\nAccessories" 
        },
        {
        "doctype": "Quotation",
        "doctype_or_field": "DocField",
        "fieldname": "order_type",
        "property": "options",
        "property_type": "Text",
        "value": "\nSales\nMaintenance\nShopping Cart\nAccessories" 
        },
        {
        "doctype": "Quotation",
        "doctype_or_field": "DocField",
        "fieldname": "status",
        "property": "options",
        "property_type": "Text",
        "value": "\nDraft\nOpen\nReplied\nOrdered\nLost\nCancelled\nExpired\nRejected" 
        },
        {
        "doctype":"Item",
        "doctype_or_field": "DocField",
        "fieldname":"delivered_by_supplier",
        "property": "default",
        "property_type": "Text",
        "value": "1"
        },
        {
        "doctype": "Sales Order",
        "doctype_or_field": "DocField",
        "fieldname": "payment_terms_template",
        "property": "allow_on_submit",
        "property_type": "Check",
        "value": "1",
        "default_value":1
        },
        {
        "doctype": "Sales Order",
        "doctype_or_field": "DocField",
        "fieldname": "payment_schedule",
        "property": "allow_on_submit",
        "property_type": "Check",
        "value": "1",
        "default_value":1
        },
        {
        "doctype": "Purchase Invoice",
        "doctype_or_field": "DocField",
        "fieldname": "payment_schedule",
        "property": "allow_on_submit",
        "property_type": "Check",
        "value": "1",
        "default_value":1
        },
        {
        "doctype": "Sales Invoice",
        "doctype_or_field": "DocField",
        "fieldname": "payment_schedule",
        "property": "allow_on_submit",
        "property_type": "Check",
        "value": "1",
        "default_value":1
        },
        {
        "doctype": "Quotation",
        "doctype_or_field": "DocField",
        "fieldname": "payment_schedule",
        "property": "allow_on_submit",
        "property_type": "Check",
        "value": "1",
        "default_value":1
        },
        {
        "doctype": "Sales Order",
        "doctype_or_field": "DocField",
        "fieldname": "shipping_rule",
        "property": "allow_on_submit",
        "property_type": "Check",
        "value": "1",
        "default_value":1
        },
        {
        "doctype": "Sales Invoice",
        "doctype_or_field": "DocField",
        "fieldname": "shipping_rule",
        "property": "allow_on_submit",
        "property_type": "Check",
        "value": "1",
        "default_value":1
        },
        {
        "doctype": "Sales Order",
        "doctype_or_field": "DocField",
        "fieldname": "shipping_rule",
        "property": "reqd",
        "property_type": "Check",
        "value": "1",
        "default_value":1
        },
        {
        "doctype": "Purchase Order",
        "doctype_or_field": "DocField",
        "fieldname": "shipping_rule",
        "property": "reqd",
        "property_type": "Check",
        "value": "1",
        "default_value":1
        },
        {
        "doctype": "Lead",
        "doctype_or_field": "DocField",
        "fieldname": "email_id",
        "property": "reqd",
        "property_type": "Check",
        "value": "1",
        "default_value":"1"
        },
        {
        "doctype": "Payment Schedule",
        "doctype_or_field": "DocField",
        "fieldname": "payment_term",
        "property": "allow_on_submit",
        "property_type": "Check",
        "value": "1",
        "default_value":1
        },
        {
        "doctype": "Payment Schedule",
        "doctype_or_field": "DocField",
        "fieldname": "description",
        "property": "allow_on_submit",
        "property_type": "Check",
        "value": "1",
        "default_value":1
        },
        {
        "doctype": "Payment Schedule",
        "doctype_or_field": "DocField",
        "fieldname": "due_date",
        "property": "allow_on_submit",
        "property_type": "Check",
        "value": "1",
        "default_value":1
        },
        {
        "doctype": "Payment Schedule",
        "doctype_or_field": "DocField",
        "fieldname": "invoice_portion",
        "property": "allow_on_submit",
        "property_type": "Check",
        "value": "1",
        "default_value":1
        },
        {
        "doctype": "Payment Schedule",
        "doctype_or_field": "DocField",
        "fieldname": "payment_amount",
        "property": "allow_on_submit",
        "property_type": "Check",
        "value": "1",
        "default_value":1
        },
        {
        "doctype": "Payment Schedule",
        "doctype_or_field": "DocField",
        "fieldname": "discount_type",
        "property": "allow_on_submit",
        "property_type": "Check",
        "value": "1",
        "default_value":1
        },
        {
        "doctype": "Payment Schedule",
        "doctype_or_field": "DocField",
        "fieldname": "discount",
        "property": "allow_on_submit",
        "property_type": "Check",
        "value": "1",
        "default_value":1
        },
        {
        "doctype": "Payment Schedule",
        "doctype_or_field": "DocField",
        "fieldname": "base_payment_amount",
        "property": "allow_on_submit",
        "property_type": "Check",
        "value": "1",
        "default_value":1
        },
        {
        "doctype": "Address",
        "doctype_or_field": "DocField",
        "fieldname": "address_type",
        "property": "options",
        "property_type": "Text",
        "value": "\nOffice\nSite"
        },
        {
        "doctype": "Lead",
        "doctype_or_field": "DocField",
        "fieldname": "address_type",
        "property": "options",
        "property_type": "Text",
        "value": "Site\nOffice\nShipping\nPersonal\nPlant\nPostal\nShop\nSubsidiary\nWarehouse\nCurrent\nPermanent\nOther\nBilling",
        "default":"Site"
        },
        {
        "doctype": "Quotation",
        "doctype_or_field": "DocField",
        "fieldname": "shipping_rule",
        "property": "reqd",
        "property_type": "Check",
        "value": "1",
        },
        {
        "doctype": "Request for Quotation Supplier",
        "doctype_or_field": "DocField",
        "fieldname": "send_email",
        "property": "in_list_view",
        "property_type": "Check",
        "value": "0",
        },
        {
        "doctype": "Request for Quotation Supplier",
        "doctype_or_field": "DocField",
        "fieldname": "send_email",
        "property": "default",
        "property_type": "Text",
        "value": "0",
        },
        {
        "doctype": "Quotation",
        "doctype_or_field": "DocField",
        "fieldname": "status",
        "property": "options",
        "property_type": "Text",
        "value": "\nDraft\nOpen\nReplied\nOrdered\nLost\nCancelled\nExpired\nPotential",

        },
        
    ],
  
    'on_setup': 'dynamic.ifi.setup.setup_ifi'
}







