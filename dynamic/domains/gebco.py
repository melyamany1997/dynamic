from __future__ import unicode_literals

data = {
    
    'custom_fields': {
        'Serial No': [
            {
                "fieldname": "serial2",
                "fieldtype": "Data",
                "insert_after": "serial_no",
                "label": "Serial No 2",
                "unique": 1,
                "in_global_search": 1,
                "in_standard_filter": 1,
                "in_preview": 1,
            },
        ],
        'Sales Invoice': [
            {
                "fieldname": "maintenance_template",
                "fieldtype": "Link",
                "options":"Maintenance Template",
                "insert_after": "delivery_note",
                "label": "Maintenance Template",
                "print_hide": 1,
            },
            {
                "fieldname": "maintenance_contract",
                "fieldtype": "Link",
                "options":"Maintenance Contract",
                "insert_after": "maintenance_template",
                "label": "Maintenance Contract",
                "print_hide": 1,
            },
        ],
        'Delivery Note': [
            {
                "fieldname": "maintenance_template",
                "fieldtype": "Link",
                "options":"Maintenance Template",
                "insert_after": "sales_team",
                "label": "Maintenance Template",
                "print_hide": 1,
            },
        ],
        'Stock Entry': [
            {
                "fieldname": "maintenance_template",
                "fieldtype": "Link",
                "options":"Maintenance Template",
                "insert_after": "is_return",
                "label": "Maintenance Template",
                "print_hide": 1,
            },
            {
                "fieldname": "installation_section",
                "fieldtype": "Section Break",
                "insert_after": "apply_putaway_rule",
                "label": "Installation Section",
               
            },
            {
                "fieldname": "installation_request",
                "fieldtype": "Link",
                "options":"Installation Request",
                "insert_after": "installation_section",
                "label": "Installation Request",
                "read_only" : 1
            },
            {
                "fieldname": "install_column_break",
                "fieldtype": "Column Break",
                "insert_after": "installation_request",
                "label": "",
               
            },
            {
                "fieldname": "installation_order",
                "fieldtype": "Link",
                "options":"Installation Order",
                "insert_after": "install_column_break",
                "label": "Installation Order",
                "read_only" : 1
            },
            {
                "fieldname": "car_installation",
                "fieldtype": "Link",
                "options":"Car Installation",
                "insert_after": "installation_order",
                "label": "Car Installation",
                "read_only" : 1
            },
        ],
        
        'Delivery Note': [
            {
                "fieldname": "installation_section",
                "fieldtype": "Section Break",
                "insert_after": "return_against",
                "label": "Installation Section",
               
            },
            {
                "fieldname": "installation_request",
                "fieldtype": "Link",
                "options":"Installation Request",
                "insert_after": "installation_section",
                "label": "Installation Request",
                "read_only" : 1
            },
            {
                "fieldname": "install_column_break",
                "fieldtype": "Column Break",
                "insert_after": "installation_request",
                "label": "",
               
            },
            {
                "fieldname": "installation_order",
                "fieldtype": "Link",
                "options":"Installation Order",
                "insert_after": "install_column_break",
                "label": "Installation Order",
                "read_only" : 1
            },
            {
                "fieldname": "car_installation",
                "fieldtype": "Link",
                "options":"Car Installation",
                "insert_after": "installation_order",
                "label": "Car Installation",
                "read_only" : 1
            },
        ],
        'Sales Order':[
            {
                "fieldname": "installation_details",
                "fieldtype": "Section Break",
                "insert_after": "items",
                "label": "Installation Details",
               
            },
             {
                "fieldname": "total_cars",
                "fieldtype": "Int",
                "insert_after": "installation_details",
                "label": "Total Cars",
            },
             {
                "fieldname": "colum_break_install_details1",
                "fieldtype": "Column Break",
                "insert_after": "total_cars",
                "label": "",
            },
            {
                "fieldname": "completed_cars",
                "fieldtype": "Int",
                "insert_after": "colum_break_install_details1",
                "label": "Completed Cars",
                "read_only" : 1,
                "no_copy" : 1,
                "allow_on_submit":1,
                "default":0
            },
            {
                "fieldname": "requested_cars",
                "fieldtype": "Int",
                "insert_after": "completed_cars",
                "label": "Requested Cars",
                "read_only" : 1,
                "no_copy" : 1,
                "allow_on_submit":1,
                "default":0
            },
            {
                "fieldname": "ordered_cars",
                "fieldtype": "Int",
                "insert_after": "requested_cars",
                "label": "Ordered Cars",
                "read_only" : 1,
                "no_copy" : 1,
                "allow_on_submit":1,
                "default":0
            },
            {
                "fieldname": "colum_break_install_details2",
                "fieldtype": "Column Break",
                "insert_after": "ordered_cars",
                "label": "",
            },
            {
                "fieldname": "pending_cars",
                "fieldtype": "Int",
                "insert_after": "colum_break_install_details2",
                "label": "Pending Cars",
                "read_only" : 1,
                "no_copy" : 1,
                "allow_on_submit":1,
                "default":0
            },
            {
                "fieldname": "not_requested_cars",
                "fieldtype": "Int",
                "insert_after": "pending_cars",
                "label": "Not Requested Cars",
                "read_only" : 1,
                "no_copy" : 1,
                "allow_on_submit":1,
                "default":0
            },
            {
                "fieldname": "not_ordered_cars",
                "fieldtype": "Int",
                "insert_after": "not_requested_cars",
                "label": "Not Ordered Cars",
                "read_only" : 1,
                "no_copy" : 1,
                "allow_on_submit":1,
                "default":0
            },
            # {
            #     "fieldname": "invoice_payment",
            #     "fieldtype": "Float",
            #     "insert_after": "advance_paid",
            #     "label": "Invoice Payment",
            #     "read_only" : 1,
            #     "no_copy" : 1,
            #     "allow_on_submit":1,
            #     "default":0
            # },
            # {
            #     "fieldname": "outstanding_amount",
            #     "fieldtype": "Float",
            #     "insert_after": "invoice_payment",
            #     "label": "Outstanding Amount",
            #     "read_only" : 1,
            #     "no_copy" : 1,
            #     "allow_on_submit":1,
            #     "default":0
            # },
            {
                "fieldname": "serial2",
                "fieldtype": "Small Text",
                "insert_after": "serial_no",
                "label": "Serial No 2",
                "length": 240,
            },
        ],
        'Purchase Receipt Item':[
            {
                "fieldname": "serial2",
                "fieldtype": "Small Text",
                "insert_after": "serial_no",
                "label": "Serial No 2",
                "length": 240,
            },
        ],

    },
    "properties": [

    ],
    "property_setters": [
        {
        "doc_type": "Serial No",
        "doctype_or_field": "DocType",
        "modified_by": "Administrator",
        "name": "Serial No-main-search_fields",
        "property": "search_fields",
        "property_type": "Data",
        "value": "item_code,serial2"
        }
    ],
    'on_setup': 'dynamic.gebco.setup.create_contract_service_item'
    
}
