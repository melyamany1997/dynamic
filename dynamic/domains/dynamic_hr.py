from __future__ import unicode_literals

data = {

    'custom_fields': {
        'Employee Checkin': [
            {
                "fieldname": "device_log",
                "fieldtype": "Link",
                "insert_after": "log_type",
                "label": "Log",
                "options": "Device Log",
                "read_only":1

            }
        ]


    },
    "properties": [

    ],
    "property_setters": [

    ],
    'on_setup': 'dynamic.dynamic_hr.setup.install_dynamic_hr'
}
