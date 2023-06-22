

from __future__ import unicode_literals

data = {

    'custom_fields': {
        'Customer':[
            {
                "label":"Parent Territory",
                "fieldname":"parent_territory",
                "fieldtype":"Link",
                "options":'Territory',
                "insert_after":"territory",
                "in_list_view":1,
                "in_standard_filter ":1
                
            },
        ],
        
    },
      "properties": [

    ],
  
    'on_setup': 'dynamic.teba.setup.setup_teba'
}







