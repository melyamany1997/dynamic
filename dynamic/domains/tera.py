from __future__ import unicode_literals


data = {

    'custom_fields': {
        "Stock Reconciliation Item":[
            {
                "label": "Item Group",
                "fieldname": "item_group",
                "fieldtype": "Link",
                "insert_after": "warehouse",
                "options" : "Item Group" , 
                "in_list_view" : "1" , 
                "columns" : "1" , 
            },
            {
                "label": "Brand",
                "fieldname": "brand",
                "fieldtype": "Link",
                "insert_after": "item_group",
                "options" : "Brand" , 
                "in_list_view" : "1" , 
                "columns" : "1" , 
            },
        ],
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
                "reqd":1
                
            },
            
            
        ],
        
        "Sales Order":[
            {
                "label": "Customer Print Name",
                "fieldname": "customer_print_name",
                "fieldtype": "Data",
                "insert_after": "order_type",
            },
             {
                "fieldname": "invoice_payment",
                "fieldtype": "Float",
                "insert_after": "advance_paid",
                "label": "Invoice Payment",
                "read_only" : 1,
                "no_copy" : 1,
                "allow_on_submit":1,
                "default":0
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
        # ],


        #  'Sales Order' :[
            # {
            #     "fieldname": "reservation",
            #     "fieldtype": "Link",
            #     "insert_after": "project",
            #     "label": "Reservation",
            #     'options' : 'Reservation',
            #     'read_only' : 1
            # },
            {
                "fieldname": "purchase_order",
                "fieldtype": "Link",
                "insert_after": "set_warehouse",
                "label": "Purchase Order",
                'options' : 'Purchase Order'
            },
            {
                "fieldname": "reservation_status",
                "fieldtype": "Select",
                "options": "\nActive\nClosed\nInvalid",
                "insert_after": "set_warehouse",
                "label": "Reservation Status",
                'read_only' : 1,
                "fetch_from": "reservation.status",
                "allow_on_submit":1 
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
                "fieldname": "opportunity",
                "fieldtype": "Link",
                "insert_after": "source",
                "label": "Opportunity",
                'options' : 'Opportunity' ,
                "reqd" : 1
            },
            
            
         ],
         'Landed Cost Item': [
            {
                "fieldname": "rate_currency",
                "fieldtype": "Currency",
                "insert_after": "rate",
                "label": "Price in supplier currency",
                'read_only' : 1
            },
               {
                "fieldname": "item_after_cost",
                "fieldtype": "Currency",
                "insert_after": "rate_currency",
                "label": "Item after cost in company Currency",
                'read_only' : 1
            },
             {
                "fieldname": "item_cost_value",
                "fieldtype": "Currency",
                "insert_after": "item_after_cost",
                "label": "Item cost value in Company Currency",
                'read_only' : 1
            },
             {
                "fieldname": "purchase_currency",
                "fieldtype": "Data",
                "insert_after": "item_cost_value",
                "label": "Purchase Currency",
                'read_only' : 1
            },
             {
                "fieldname": "currency",
                "fieldtype": "Data",
                "insert_after": "item_cost_valu",
                "label": "Invocie Currency Factor",
                'read_only' : 1
            },
        ],
         "Landed Cost Voucher" :[
            {
                "fieldname": "cost_set_section",
                "fieldtype": "Section Break",
                "insert_after": "items",
                "label": "Cost Section",
               
            },
             {
                "fieldname": "cost_child_table",
                "fieldtype": "Table",
                "insert_after": "cost_set_section",
                "label": "Charges",
                "options" :"Landed Cost Voucher Child"
            },


        ] ,
        'Landed Cost Taxes and Charges':[
             {
                "fieldname": "line_name",
                "fieldtype": "Data",
                "insert_after": "base_amount",
                "label": "Line Name",
                "read_only" : 1
               

            },
             {
                "fieldname": "docment_type",
                "fieldtype": "Data",
                "insert_after": "line_name",
                "label": "Document Type",
                "read_only" : 1
               

            },
             {
                "fieldname": "docment_name",
                "fieldtype": "Data",
                "insert_after": "docment_type",
                "label": "Document Name",
                "read_only" : 1
               

            },

        ],

        
        'Company':[
            {
                "fieldname": "sales_return_account",
                "fieldtype": "Link",
                "options":"Account",
                "insert_after": "unrealized_profit_loss_account",
                "label": "Sales Return Account"
            },
        ],
        'Item Group':[
            {
                "fieldname": "code",
                "fieldtype": "Data",
                "insert_after": "column_break_5",
                "label": "Group Code",
                "unique": 1,
                "reqd":1

            },
        ],
        'Lead':[
             {
            "fieldname": "phone_no",
            "fieldtype": "Data",
            "in_global_search": 1,
            "in_standard_filter": 1,
            "insert_after": "email_id",
            "label": "Phone No",
            "translatable": 1,
            "unique": 1,
            "reqd": 1
            }
        ] ,
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
                "reqd":1
                
            },
            {
                 "label" :"Opportunity Name" ,
                 "fieldname": "opportunity_name",
                 "fieldtype": "Data",
                 "insert_after": "customer_name",
                 "in_global_search" :1, 
                
            },
        ],
        'Stock Settings':[
            {
                "fieldname": "email_section",
                "fieldtype": "Section Break",
                "insert_after": "stock_auth_role"
            },
            {
                "fieldname": "email_setting",
                "fieldtype": "Table",
                "options":"Email Setting",
                "insert_after": "email_section",
                "label": "Email Setting",
                "translatable": 1,
            },
            {
                "fieldname": "reservation_setting_section",
                "fieldtype": "Section Break",
                "insert_after": "email_setting"
            },
            {
                "fieldname": "reservation_setting",
                "fieldtype": "Table",
                "options":"Reservation Child",
                "insert_after": "reservation_setting_section",
                "label": "Reservation Setting",
                "translatable": 1,
            }
        ],
        'Material Request':[
            {
                "fieldname": "project_name",
                "fieldtype": "Link",
                "options": "Project Name",
                "insert_after": "material_request_type",
                "label": "Project Name"
            },
            {
                "fieldname": "m_created_by",
                "fieldtype": "Link",
                "options": "User",
                "insert_after": "company",
                "label": "Created By",
                "read_only":1,
                "default":"__user"
            },

            {
                "fieldname": "cost_center",
                "fieldtype": "Link",
                "options": "Cost Center",
                "insert_after": "m_created_by",
                "label": "Cost Center"
            },
            {
                "fieldname": "quotation",
                "fieldtype": "Link",
                "options": "Supplier Quotation",
                "insert_after": "project_name",
                "label": "Supplier Quotation",
                "read_only" :1 ,
           
            },
             {
                "fieldname": "has_quotation",
                "fieldtype": "Check",
                "insert_after": "quotation",
                "label": "Has Quotation",
                "read_only" :1 ,
                "in_list_view" :1 ,
                "in_standard_filter" :1
            },
            {
                "label": "Customer / Lead Name",
                "fieldname": "customer_name",
                "fieldtype": "Data",
                "insert_after": "project_name",
                "read_only" :1 ,
            },
            {
                "label": "Opportunity",
                "fieldname": "opportunity",
                "fieldtype": "Link",
                "options": "Opportunity",
                "insert_after": "customer_name",
                "read_only" :1 ,
            },

        ],
        "Appointment":[

             {
                "fieldname": "created_on",
                "fieldtype": "Date",
                "insert_after": "calendar_event",
                "label": "Created On",
                "read_only" :1 ,
                "in_list_view" :1 ,
                "in_standard_filter" :1
            }
        ],

        'Sales Order Item':[
             {
            "fieldname": "reservation",
            "fieldtype": "Link",
            "options": "Reservation",
            "insert_after": "section_break_5",
            "label": "Reservation",
            # "in_list_view":1,
            "allow_on_submit":1,
            "read_only" : 1,
            "no_copy":1
            },
            {
            "fieldname": "reservation_status",
            "fieldtype": "Data",
            "insert_after": "reservation",
            "label": "Reservation Status",
            # "in_list_view":1,
            "allow_on_submit":1,
            "read_only" : 1,
            "no_copy":1
            },
            {
            "fieldname": "item_warehouse",
            "fieldtype": "Link",
            "insert_after": "item_name",
            "label": "Item Warehouse",
            'options' : 'Warehouse'
            # "in_list_view":1,
            },
            {
            "fieldname": "item_purchase_order",
            "fieldtype": "Link",
            "insert_after": "item_warehouse",
            "label": "Purchase Order",
            'options' : 'Purchase Order'
            # "in_list_view":1,
            },
            {
            "fieldname": "schedule_date",
            "fieldtype": "Date",
            "insert_after": "item_purchase_order",
            "label": "Required By",
            'options' : 'Purchase Order',
            'fetch_from':'item_purchase_order.schedule_date',
            "read_only" : 1,
            "fetch_if_empty": 1
            },
            {
                "fieldname": "sub_uom",
                "fieldtype": "Link",
                "insert_after": "picked_qty",
                "label": "Sub Uom",
                "options" : 'UOM',
                "read_only":1,
            
            },
            {
                "fieldname": "sub_uom_conversation_factor",
                "fieldtype": "Float",
                "insert_after": "sub_uom",
                "label": "Sub Uom Conversion Factor",
                "read_only":1
            },
            {
                "fieldname": "qty_as_per_sub_uom",
                "fieldtype": "Float",
                "insert_after": "sub_uom_conversation_factor",
                "label": "QTY As Per Sub Uom",
                "read_only":1
            
            },
            {
                "fieldname": "so_approved_qty",
                "fieldtype": "Section Break",
                "insert_after": "stock_qty",
                "label": "Approved Qty",
            },
            {
                "fieldname": "approved_qty",
                "fieldtype": "Float",
                "insert_after": "so_approved_qty",
                "label": "Approved QTY",
                "read_only":1,
                "no_copy":1
            },
            {
                "fieldname": "remaining_qty",
                "fieldtype": "Float",
                "insert_after": "approved_qty",
                "label": "Remaining Qty",
                "read_only":1,
                "no_copy":1
            }

        ], 
        "Purchase Order Item":[
             {
                "fieldname": "sub_uom",
                "fieldtype": "Link",
                "insert_after": "stock_uom",
                "label": "Sub Uom",
                "options" : 'UOM',
                "read_only":1,
            
            },
            {
                "fieldname": "sub_uom_conversation_factor",
                "fieldtype": "Float",
                "insert_after": "sub_uom",
                "label": "Sub Uom Conversion Factor",
                "read_only":1
            },
            {
                "fieldname": "qty_as_per_sub_uom",
                "fieldtype": "Float",
                "insert_after": "sub_uom_conversation_factor",
                "label": "QTY As Per Sub Uom",
                "read_only":1
            
            }
        ],
        "Delivery Note Item":[
             {
                "fieldname": "sub_uom",
                "fieldtype": "Link",
                "insert_after": "stock_uom",
                "label": "Sub Uom",
                "options" : 'UOM',
                "read_only":1,
            
            },
            {
                "fieldname": "sub_uom_conversation_factor",
                "fieldtype": "Float",
                "insert_after": "sub_uom",
                "label": "Sub Uom Conversion Factor",
                "read_only":1
            },
            {
                "fieldname": "qty_as_per_sub_uom",
                "fieldtype": "Float",
                "insert_after": "sub_uom_conversation_factor",
                "label": "QTY As Per Sub Uom",
                "read_only":1
            
            },
            {
                "fieldname": "sales_order_approval",
                "fieldtype": "Link",
                "insert_after": "pick_list_item",
                "label": "Sales Order Approval",
                "options":"Sales Order Approval",
                "read_only":1
            }
        ],

        #New Request Update 1- Update Cost Center Warehouse
        "Cost Center" :[
            {
                    "fieldname": "payment_naming",
                    "fieldtype": "Data",
                    "insert_after": "old_parent",
                    "label": "Branch Options"   

            },
            {
                    "fieldname": "branch_section",
                    "fieldtype": "Section Break",
                    "insert_after": "old_parent",
                    "label": "Branch Options"   

            },
            
             {
                "fieldname": "warehouse",
                "fieldtype": "Link",
                "insert_after": "intermediate_warehouse",
                "label": "Warehouse",
                'options' : 'Warehouse'
            
            },
              {
                "fieldname": "manager",
                "fieldtype": "Table",
                "insert_after": "warehouse",
                "label": "Branch managers",
                'options' : 'Branch Managers'
            
            },

        ] ,
        "Quotation Item":[
            {
                "fieldname": "sub_uom",
                "fieldtype": "Link",
                "insert_after": "stock_uom",
                "label": "Sub Uom",
                "options" : 'UOM',
                "read_only":1,
            
            },
            {
                "fieldname": "sub_uom_conversation_factor",
                "fieldtype": "Float",
                "insert_after": "sub_uom",
                "label": "Sub Uom Conversion Factor",
                "read_only":1
            },
            {
                "fieldname": "qty_as_per_sub_uom",
                "fieldtype": "Float",
                "insert_after": "sub_uom_conversation_factor",
                "label": "QTY As Per Sub Uom",
                "read_only":1
            
            }
        ],
          "Stock Entry":[
             {
                "fieldname": "ds_warehouse",
                "fieldtype": "Link",
                "insert_after": "stock_entry_type",
                "label": "Target WareHouse",
                "options" : 'Warehouse',
                "depends_on":"eval:doc.add_to_transit=='1'",
                "read_only":0,
            
            },

          ],
        

        "Stock Entry Detail":[
            {
                "fieldname": "sub_uom",
                "fieldtype": "Link",
                "insert_after": "transfer_qty",
                "label": "Sub Uom",
                "options" : 'UOM',
                "read_only":1,
            
            },
            {
                "fieldname": "sub_uom_conversation_factor",
                "fieldtype": "Float",
                "insert_after": "sub_uom",
                "label": "Sub Uom Conversion Factor",
                "read_only":1
            },
            {
                "fieldname": "qty_as_per_sub_uom",
                "fieldtype": "Float",
                "insert_after": "sub_uom_conversation_factor",
                "label": "QTY As Per Sub Uom",
                "read_only":1
            
            }
        ],
         "Purchase Receipt Item":[
            {
                "fieldname": "sub_uom",
                "fieldtype": "Link",
                "insert_after": "stock_qty",
                "label": "Sub Uom",
                "options" : 'UOM',
                "read_only":1,
            
            },
            {
                "fieldname": "sub_uom_conversation_factor",
                "fieldtype": "Float",
                "insert_after": "sub_uom",
                "label": "Sub Uom Conversion Factor",
                "read_only":1
            },
            {
                "fieldname": "qty_as_per_sub_uom",
                "fieldtype": "Float",
                "insert_after": "sub_uom_conversation_factor",
                "label": "Recived QTY As Per Sub Uom",
                "read_only":1
            
            }
        ],
        "UOM Conversion Detail":[
            {
                "fieldname": "is_sub_uom",
                "fieldtype": "Check",
                "insert_after": "conversation_factor",
                "label": "Is Sub Uom",
                "in_list_view":1
            
            }
        ],
        "Item":[
            {
                "fieldname": "color",
                "fieldtype": "Link",
                "insert_after": "brand",
                "label": "Color",
                "options":"Color"
            },
            {
                "fieldname": "size",
                "fieldtype": "Link",
                "insert_after": "color",
                "label": "Size",
                "options":"Size"

            },
            {
                "fieldname": "cbreak12",
                "fieldtype": "Column Break",
                "insert_after": "size",
            },
            {
                "fieldname": "specs",
                "fieldtype": "Data",
                "insert_after": "cbreak12",
                "label": "Specification",
            },
            {
                "fieldname": "cutting_type",
                "fieldtype": "Link",
                "insert_after": "specs",
                "label": "Cutting Type",
                "options":"Cutting Type"
            }
        ],
        "Mode of Payment":[
            {
                "fieldname":"deduction_secion",
                "insert_after":"accounts",
                "fieldtype": "Section Break",
                "label":"Deduction Section"
            },
            {
                "fieldname": "has_deduct",
                "fieldtype": "Check",
                "insert_after": "deduction_secion",
                "label": "Has Deduct"
            },
            {
                "fieldname": "deduct_percentage",
                "fieldtype": "Float",
                "insert_after": "has_deduct",
                "label": "Deduction Percentage",
                "mandatory_depends_on":"eval:doc.has_deduct==1",
                "default":""
            },
            {
                "fieldname":"deduct_column_break",
                "insert_after":"deduct_percentage",
                "fieldtype": "Column Break"
            },
            {
                "fieldname": "recived_account",
                "fieldtype": "Link",
                "insert_after": "deduct_column_break",
                "label": "Recive Account",
                "options":"Account",
                "mandatory_depends_on":"eval:doc.has_deduct==1"
            },
            {
                "fieldname": "cost_center",
                "fieldtype": "Link",
                "insert_after": "deduct_column_break",
                "label": "Cost Center",
                "options":"Cost Center",
                "mandatory_depends_on":"eval:doc.has_deduct==1"
            },
            {
                "fieldname":"naming",
                "fieldtype":"Select",
                "label":"Naming Template",
                "insert_after":"type",
                "options":"\nProjects-.YYYY.-\nHeliopolis-.YYYY.-\nNew Cairo-.YYYY.-\nZayed-.YYYY.-\nMohandseen-.YYYY.-\nMain-.YYYY.-"
            }
        ],
        "Payment Entry Deduction":[
            {
                "fieldname": "Percentage",
                "fieldtype": "Float",
                "insert_after": "amount",
                "label": "Percentage",
            },
        
        ],
        "Payment Entry":[
            {
                "fieldname":"mode_of_payment_naming",
                "fieldtype":"Data",
                "insert_after":"title",
                "hidden":1,
                "no_copy":1
            }
        ],
        "Asset Movement Item":[
            {
                "fieldname": "cost_center",
                "fieldtype": "Link",
                "insert_after": "to_employee",
                "label": "Cost Center",
                "options":"Cost Center"
            },
        ],
        "Pay and Receipt Account":[
            #  {
            #     "label": "Cost Center",
            #     "fieldname": "cost_center",
            #     "fieldtype": "Link",
            #     "insert_after": "amount",
            #     "options":"Cost Center",
            #     "in_list_view":1,
            #     "columns":1
            # },
        ]

    },
    # "properties": [
        
    # ],
    "properties": [
        {
        "doctype": "Item",
        "doctype_or_field": "DocField",
        "fieldname": "item_code",
        "property": "read_only",
        "property_type": "Check",
        "value": "1"
        },
        {
        "doctype": "Quotation",
        "doctype_or_field": "DocField",
        "fieldname": "opportunity",
        "property": "reqd",
        "property_type": "Check",
        "value": "1"
        },
        {
        "doctype": "Sales Order",
        "doctype_or_field": "DocField",
        "fieldname": "set_warehouse",
        "property": "reqd",
        "property_type": "Check",
        "value": "0"
        },
        {
        "doctype": "Sales Order Item",
        "doctype_or_field": "DocField",
        "fieldname": "warehouse",
        "property": "read_only",
        "property_type": "Check",
        "value": "0"
        },
        {
        "doctype": "Material Request",
        "doctype_or_field": "DocField",
        "fieldname": "status",
        "property": "options",
        "property_type": "Text",
        "value": "\nDraft\nSubmitted\nStopped\nCancelled\nPending\nRequested\nPartially Ordered\nPartially Received\nOrdered\nIssued\nTransferred\nReceived"
        },
        {
        "doctype": "Material Request",
        "doctype_or_field": "DocField",
        "fieldname": "material_request_type",
        "property": "options",
        "property_type": "Text",
        "value": "\nPurchase\nMaterial Transfer\nMaterial Issue\nManufacture\nCustomer Provided\nPrice Request"
        },
        {
        "doctype": "Sales Order",
        "doctype_or_field": "DocField",
        "fieldname": "cost_center",
        "property": "reqd",
        "property_type": "Check",
        "value": "1"
        },
        {
        "doctype": "Sales Invoice",
        "doctype_or_field": "DocField",
        "fieldname": "cost_center",
        "property": "reqd",
        "property_type": "Check",
        "value": "1"
        },
        {
        "doctype": "Material Request",
        "doctype_or_field": "DocField",
        "fieldname": "cost_center",
        "property": "reqd",
        "property_type": "Check",
        "value": "1"
        },
        {
        "doctype": "Sales Order Item",
        "doctype_or_field": "DocField",
        "fieldname": "discount_amount",
        "property": "in_list_view",
        "property_type": "Check",
        "value": "1"
        },
        {
        "doctype": "Sales Order Item",
        "doctype_or_field": "DocField",
        "fieldname": "discount_amount",
        "property": "columns",
        "property_type": "Int",
        "value": "1"
        },
        {
            "doctype": "Sales Order Item",
            "doctype_or_field": "DocField",
            "fieldname": "qty",
            "property": "columns",
            "property_type": "Int",
            "value": "1"
        },
        {
            "doctype": "Sales Order Item",
            "doctype_or_field": "DocField",
            "fieldname": "rate",
            "property": "columns",
            "property_type": "Int",
            "value": "1"
        },
        {
        "doctype": "Sales Order Item",
        "doctype_or_field": "DocField",
        "fieldname": "amount",
        "property": "columns",
        "property_type": "Int",
        "value": "2"
        },
        {
        "doctype": "Sales Order Item",
        "doctype_or_field": "DocField",
        "fieldname": "description",
        "property": "read_only",
        "property_type": "Check",
        "value": "1"
        },
        {
            "doctype": "Stock Reconciliation Item",
            "doctype_or_field": "DocField",
            "fieldname": "valuation_rate",
            "property": "columns",
            "property_type": "Int",
            "value": "1"
        },
        {
            "doctype": "Stock Reconciliation Item",
            "doctype_or_field": "DocField",
            "fieldname": "qty",
            "property": "columns",
            "property_type": "Int",
            "value": "1"
        },
    ],
  
    'on_setup': 'dynamic.terra.setup.create_terra_scripts'
}