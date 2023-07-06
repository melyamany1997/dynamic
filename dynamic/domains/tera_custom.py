from __future__ import unicode_literals


data = {

    'custom_fields': {
        'Opportunity':[
            {
            "label" :"Customer" ,
            "fieldname": "customer",
            "fieldtype": "Link",
            "insert_after": "party_name",
            "options" :"Customer", 
            # "read_only" : 1,
            },
            {
            "fieldname": "phone_no",
            "fieldtype": "Data",
            "insert_after": "source",
            "label": "Phone No",
            "reqd": 0
          
            },
            {
                "label": "Cost Center",
                "fieldname": "cost_center",
                "fieldtype": "Link",
                "insert_after": "opportunity_from",
                "options" : "Cost Center" , 
                "read_only" : 0,
                "allow_on_submit":0,
                "reqd":0
            },
            {
                 "label" :"Opportunity Name" ,
                 "fieldname": "opportunity_name",
                 "fieldtype": "Data",
                 "insert_after": "customer_name",
                 "in_global_search" :1, 
                
            },
        ],

    },

    "properties": [
      
    ],
  
    # 'on_setup': 'dynamic.terra.setup.create_terra_scripts'
}