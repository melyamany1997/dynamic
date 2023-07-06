

from __future__ import unicode_literals
import frappe
from frappe import _

data = {

    'custom_fields': {
        'Company':[
            # {
            #     "label":_("Notification Cheque Role"),
            #     "fieldname":"notification_cheque_role",
            #     "fieldtype":"Link",
            #     "options":"Role",
            #     "insert_after":"rejected_cheques_bank_account", 
            # },
            
        ],
        'Supplier':[
            {
                "label":_("Supplier Code"),
                "fieldname":"supplier_code",
                "fieldtype":"Data",
                "insert_after":"supplier_name", 
                "in_global_search":1, 
            },
            
        ],
        'Customer':[
            {
                "label":_("Customer Code"),
                "fieldname":"customer_code",
                "fieldtype":"Data",
                "insert_after":"customer_name", 
                "in_global_search":1, 
            },
            
        ],
        'Warehouse':[
            {
                "label":_("Warehouse Code"),
                "fieldname":"warehouse_code",
                "fieldtype":"Data",
                "insert_after":"parent_warehouse", 
                "in_global_search":1, 
            },
            
        ],
        
        'Journal Entry':[
            {
                "label":_("Notebook No"),
                "fieldname":"notebook_no",
                "fieldtype":"Data",
                "insert_after":"multi_currency", 
            },
            {
                "label":_("Main Currency"),
                "fieldname":"main_currency",
                "fieldtype":"Check",
                "insert_after":"voucher_type", 
            },
            {
                "label":_("Account Currency"),
                "fieldname":"account_currency",
                "fieldtype":"Link",
                "insert_after":"main_currency",  
                "options":"Currency", 

            },
            
        ],
        'Selling Settings':[
            {
                "label":_("Sales Serries"),
                "fieldname":"sales_series_section",
                "fieldtype":"Section Break",
                "insert_after":"allow_sales_order_creation_for_expired_quotation", 
            },
            {
                "label":_("Series Role"),
                "fieldname":"series_role",
                "fieldtype":"Table",
                "options":"Sales Naming Series Role",
                "insert_after":"sales_series_section", 
            },
            
        ],
        
        
    },
      "properties": [

    ],
  
    # 'on_setup': 'dynamic.teba.setup.setup_teba'
}







