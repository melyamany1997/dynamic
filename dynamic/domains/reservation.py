

from __future__ import unicode_literals
import frappe
from frappe import _

data = {

    'custom_fields': {
        'Sales Order':[
            {
                "label":_("Reservation"),
                "fieldname":"reservation_check",
                "fieldtype":"Check",
                "insert_after":"set_warehouse",
                
            },
        ],
        'Sales Order Item':[
             {
            "label": _("Reservation"),
            "fieldname": "reservation",
            "fieldtype": "Link",
            "options": "Reservation",
            "insert_after": "section_break_5",
            "allow_on_submit":1,
            "read_only" : 1,
            "no_copy":1
            },
            {
            "label": _("Reservation Status"),
            "fieldname": "reservation_status",
            "fieldtype": "Data",
            "insert_after": "reservation",
            "allow_on_submit":1,
            "read_only" : 1,
            "no_copy":1
            },
        ],
        
    },
      "properties": [

    ],
  
    # 'on_setup': 'dynamic.teba.setup.setup_teba'
}







