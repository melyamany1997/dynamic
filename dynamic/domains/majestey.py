from __future__ import unicode_literals

data = {

    'custom_fields': {
        'Delivery Note': [
            {
                "label": "Voucher Number",
                "fieldname": "voucher_number",
                "fieldtype": "Data",
                "insert_after": "customer",
            }
        ],
        'Stock Entry': [
            {
                "label": "Voucher Number",
                "fieldname": "voucher_number",
                "fieldtype": "Data",
                "insert_after": "stock_entry_type",
            }
        ],

       
    },
    "properties": [
       
    ],
    "property_setters": [

    ],
    # 'on_setup': 'dynamic.majestey.setup.install_majestey'
}
