from __future__ import unicode_literals

data = {

    'custom_fields': {
        "Stock Entry Detail": [
            {
                "fieldname": "sales_price",
                "fieldtype": "Float",
                "insert_after": "qty",
                "label": "Sales Price",
            },
            {
                "fieldname": "total_sales_price",
                "fieldtype": "Float",
                "insert_after": "sales_price",
                "label": "Total Sales Price",
                "read_only": 1
            },
        ],
        "Stock Entry": [
            {
                "fieldname": "total_entry_sales_price",
                "fieldtype": "Float",
                "insert_after": "total_outgoing_value",
                "label": "Total Sales Price",
                "read_only": 1
            },
            {
                "fieldname": "attention",
                "fieldtype": "Text",
                "insert_after": "is_opening",
                "label": "Attention",
                "allow_on_submit": 1
            },
        ]

    },





}
