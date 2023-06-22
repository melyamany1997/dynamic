
from __future__ import unicode_literals

data = {
'custom_fields': {
        'Stock Entry': [
            {
                "label": "Cost Center",
                "fieldname": "cost_center",
                "fieldtype": "Link",
                "options":"Cost Center",
                "insert_after": "stock_entry_type",
            },
            {
                "label": "Permission Number",
                "fieldname": "permission_number",
                "fieldtype": "Data",
                "insert_after": "cost_center",
            },
        ],
}
}