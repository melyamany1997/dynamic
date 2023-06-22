from __future__ import unicode_literals


data = {

    'custom_fields': {
       "Batch":[
        {
            "fieldname":"barcode",
            "fieldtype":"Data",
            "insert_after":"item",
            "label":"Barcode",
            "in_global_search": 1,
            "in_standard_filter": 1
        }
       ],
       "Sales Invoice":[
            # {
            #     "fieldtype":"Column Break",
            #     "fieldname":"colbracodebreak",
            #     "insert_after":"scan_barcode"
            # },
            {
                "fieldname":"batch_barcode",
                "fieldtype":"Link",
                "options":"Batch",
                "insert_after":"scan_barcode",
                "label":"Batch barcode"
            }
        
       ],
       "Purchase Receipt":[
            {
                "fieldname":"batch_barcode",
                "fieldtype":"Link",
                "options":"Batch",
                "insert_after":"scan_barcode",
                "label":"Batch barcode"
            }
       ],
       "Purchase Invoice":[
            {
                "fieldname":"batch_barcode",
                "fieldtype":"Link",
                "options":"Batch",
                "insert_after":"scan_barcode",
                "label":"Batch barcode"
            }
       ],
       "Purchase Order":[
            {
                "fieldname":"batch_barcode",
                "fieldtype":"Link",
                "options":"Batch",
                "insert_after":"scan_barcode",
                "label":"Batch barcode"
            }
       ],
       "Sales order":[
            {
                "fieldname":"batch_barcode",
                "fieldtype":"Link",
                "options":"Batch",
                "insert_after":"scan_barcode",
                "label":"Batch barcode"
            }
       ],
       "Stock Entry":[
            {
                "fieldname":"batch_barcode",
                "fieldtype":"Link",
                "options":"Batch",
                "insert_after":"scan_barcode",
                "label":"Batch barcode"
            }
       ]
    },
    # "properties": [
        
    # ],
    "properties": [
       
    ],
#     "property_setters": [
#     {
#         "doc_type": "Batch",
#         "doctype_or_field": "DocType",
#         "name": "Batch-main-search_fields",
#         "owner": "Administrator",
#         "property": "search_fields",
#         "property_type": "Data",
#         "value": "barcode"
#     }
#  ],
  
   'on_setup': 'dynamic.doctor_textile.setup.create_scripts'
}