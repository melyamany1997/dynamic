

data = {

    'custom_fields': {
        'Purchase Receipt Item': [
            {
                "label": "Actual Received Qty",
                "fieldname": "actual_received_qty",
                "fieldtype": "Float",
                "insert_after": "uom",
                "read_only":1

            }
        ]


    },

    # 'on_setup': 'dynamic.dynamic_hr.setup.install_dynamic_hr'
}