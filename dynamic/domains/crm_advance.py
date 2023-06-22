from __future__ import unicode_literals





data = {

    'custom_fields': {
        'Lead':[
             {
            "fieldname": "phone_no",
            "fieldtype": "Data",
            "in_global_search": 1,
            "in_standard_filter": 1,
            "insert_after": "email_id",
            "label": "Phone NO",
            "translatable": 1,
            "unique": 1,
            "reqd": 1,
            }
        ] ,

        'Quotation' :[
             {
                "fieldname": "material_reuqest",
                "fieldtype": "Link",
                "insert_after": "customer_name",
                "label": "Material Request",
                "options" : "Material Request" , 
                "read_only" : 0,
                "allow_on_submit":0,      
            },
            {
                "fieldname": "advance_paid",
                "fieldtype": "Currency",
                "insert_after": "in_words",
                "label": "Advance Paid",
                'options' : 'party_account_currency',
                'default' : '0' ,
                'hidden' : 0 ,
                'read_only' : 1 ,
                'no_copy' : 1 ,
                'allow_on_submit' : 1 ,
            },
            {
                "fieldname": "party_account_currency",
                "fieldtype": "Link",
                "insert_after": "advance_paid",
                "label": "Party Account Currency",
                'options' : 'Currency',
                'hidden' : 1 ,
                'read_only' : 1 ,
                'no_copy' : 1 ,
                'allow_on_submit' : 1 ,
            },
            {
                "fieldname": "outstand_amount",
                "fieldtype": "Float",
                "insert_after": "source",
                "label": "Outstand Amount",
                'hidden' : 0 ,
                'read_only' : 1 ,
                'no_copy' : 1 ,
                'allow_on_submit' : 1 ,
            },
             # quotation payment fields
            {
                "fieldname": "advance_payments",
                "fieldtype": "Section Break",
                "insert_after": "terms",
                "label": "Advance Payments",
            },
            {
                "fieldname": "allocate_advances_automatically",
                "fieldtype": "Check",
                "insert_after": "advance_payments",
                "label": "Allocate Advances Automatically (FIFO)",
                'default' : '0' ,
                'hidden' : 0 ,
                'read_only' : 0 ,
                'no_copy' : 1 ,
                'allow_on_submit' : 0 ,
            },
            {
                "fieldname": "get_advances",
                "fieldtype": "Button",
                "insert_after": "allocate_advances_automatically",
                "label": "Get Advances Received",
                'hidden' : 0 ,
                'read_only' : 0 ,
                'no_copy' : 0 ,
                'allow_on_submit' : 0 ,
            },
            {
                "fieldname": "advances",
                "fieldtype": "Table",
                "insert_after": "get_advances",
                "options":"Sales Invoice Advance",
                "label": "Advances",
                'hidden' : 0 ,
                'read_only' : 0 ,
                'no_copy' : 1 ,
                'allow_on_submit' : 0 ,
            },
            {
                "fieldname": "base_write_off_amount",
                "fieldtype": "Currency",
                "insert_after": "base_rounded_total",
                "options":"Company:company:default_currency",
                "label": "Write Off Amount (Company Currency)",
                'default' : '0' ,
                'hidden' : 0 ,
                'read_only' : 1 ,
                'no_copy' : 1 ,
                'allow_on_submit' : 1 ,
            },
            {
                "fieldname": "total_advance",
                "fieldtype": "Currency",
                "insert_after": "rounded_total",
                "options":"party_account_currency",
                "label": "Total Advance",
                'default' : '0' ,
                'hidden' : 0 ,
                'read_only' : 1 ,
                'no_copy' : 1 ,
                'allow_on_submit' : 1 ,
            },
            {
                "fieldname": "write_off_amount",
                "fieldtype": "Currency",
                "insert_after": "total_advance",
                "options":"currency",
                "label": "Write Off Amount",
                'default' : '0' ,
                'hidden' : 0 ,
                'read_only' : 1 ,
                'no_copy' : 1 ,
                'allow_on_submit' : 1 ,
            },
            {
                "fieldname": "is_return",
                "fieldtype": "Check",
                "insert_after": "write_off_amount",
                "options":"currency",
                "label": "is Return",
                'default' : '0' ,
                'hidden' : 1 ,
                'read_only' : 1 ,
                'no_copy' : 1 ,
                'allow_on_submit' : 1 ,
            },

            {
                "fieldname": "outstanding_amount",
                "fieldtype": "Float",
                "insert_after": "invoice_payment",
                "label": "Outstanding Amount",
                "read_only" : 1,
                "no_copy" : 1,
                "allow_on_submit":1,
                "default":0
            },
            {
                "label": "Cost Center",
                "fieldname": "cost_center",
                "fieldtype": "Link",
                "insert_after": "order_type",
                "options" : "Cost Center" , 
                "read_only" : 0,
                "allow_on_submit":0,
                
            },
            
            
        ],

        
        'Customer':[
             {
            "fieldname": "phone_no",
            "fieldtype": "Data",
            "in_global_search": 1,
            "in_standard_filter": 1,
            "insert_after": "tax_category",
            "label": "Phone No",
            "translatable": 1,
            "unique": 1,
            "fetch_if_empty": 1,
            "fetch_from": "lead_name.phone_no", 
            "reqd": 1
            }
        ],
        'Opportunity':[

            {
                 "fieldname": "customer",
                 "fieldtype": "Link",
                  "insert_after": "party_name",
                 "label" :"Custom" ,
                 "options" :"Customer", 
                 "read_only" : 1
                
            },
             {
            "fieldname": "phone_no",
            "fieldtype": "Data",
            "in_global_search": 1,
            "in_standard_filter": 1,
            "insert_after": "source",
            "label": "Phone No",
            "translatable": 1,
            # "unique": 1,
            "fetch_if_empty": 1,
            "reqd": 1,
            "fetch_from": "party_name.phone_no" 
            },
            {
                "label": "Cost Center",
                "fieldname": "cost_center",
                "fieldtype": "Link",
                "insert_after": "phone_no",
                "options" : "Cost Center" , 
                "read_only" : 0,
                "allow_on_submit":0,
                
            },
            {
                 "label" :"Opportunity Name" ,
                 "fieldname": "opportunity_name",
                 "fieldtype": "Data",
                 "insert_after": "customer_name",
                 "in_global_search" :1, 
                
            },
        ],
      
         
        
        
    },

    "properties": [
        {
        "doctype": "Lead",
        "doctype_or_field": "DocField",
        "fieldname": "lead_name",
        "property": "in_global_search",
        "property_type": "Check",
        "value": "1"
        },
    ],
  
    'on_setup': 'dynamic.crm_advance.setup._setup'
}