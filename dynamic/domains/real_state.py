

from __future__ import unicode_literals
import frappe
from frappe import _

data = {

    'custom_fields': {
        'Item':[
            {
                "label":_("Unit Info"),
                "fieldname":"unit_info",
                "fieldtype":"Section Break",
                "insert_after":"image", 
            },
            {
                "label":_("Unit No"),
                "fieldname":"unit_no",
                "fieldtype":"Int",
                "insert_after":"unit_info", 
            },
            {
                "label":_("Unit Area"),
                "fieldname":"unit_area",
                "fieldtype":"Float",
                "insert_after":"unit_no", 
            },
            {
                "label":_("Unit Floor"),
                "fieldname":"unit_floor",
                "fieldtype":"Int",
                "insert_after":"unit_area", 
            },
            {
                "label":_("Reserved"),
                "fieldname":"reserved",
                "fieldtype":"Check",
                "insert_after":"unit_floor", 
                "read_only":"1", 
            },
            {
                "label":_("Unit details"),
                "fieldname":"unit_details",
                "fieldtype":"Small Text",
                "insert_after":"reserved", 
            },
        ],
        
    },
      "properties": [

    ],
  
    # 'on_setup': 'dynamic.teba.setup.setup_teba'
}







