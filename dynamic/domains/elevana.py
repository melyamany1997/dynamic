from __future__ import unicode_literals

data = {

    'custom_fields': {
        'Sales Person': [
            {
                "label": "Commission Template",
                "fieldname": "commission_template",
                "fieldtype": "Link",
                "insert_after": "employee",
                "options": "Commission Template",
            }
        ],
        'Lead': [
            {
                "fieldname": "sales_person",
                "fieldtype": "Link",
                "insert_after": "campaign_name",
                "label": "Sales Person",
                "options": "Sales Person",
                "permlevel": "1"
            }
        ],

        'Opportunity': [
            {
                "fieldname": "sales_person",
                "fieldtype": "Link",
                "insert_after": "source",
                "label": "Sales Person",
                "options": "Sales Person",
                # "permlevel":"1"
            }
        ],
        'User': [
            {
                "fieldname": "extension",
                "fieldtype": "Data",
                "insert_after": "last_name",
                "label": "User Extension",
                "unique": "1",
            },
        ],
        'Customer': [
            {
                "fieldname": "sales_person",
                "fieldtype": "Link",
                "insert_after": "opportunity_name",
                "label": "Sales Person",
                "options": "Sales Person",
                # "permlevel":"1"
            },
            {
                "fieldname": "ref_doctype",
                "fieldtype": "Link",
                "insert_after": "extension",
                "label": "Reference Type",
                "options": "DocType",
                "read_only": "1",
            },
            {
                "fieldname": "ref_docname",
                "fieldtype": "Dynamic Link",
                "insert_after": "ref_doctype",
                "label": "Reference Name",
                "options": "ref_doctype",
                "read_only": "1",
            }
        ],

        'Sales Partner': [
            {
                "fieldname": "ref_doctype",
                "fieldtype": "Link",
                "insert_after": "commission_rate",
                "label": "Reference Type",
                "options": "DocType",
                "read_only": "1",
            },
            {
                "fieldname": "ref_docname",
                "fieldtype": "Dynamic Link",
                "insert_after": "ref_doctype",
                "label": "Reference Name",
                "options": "ref_doctype",
                "read_only": "1",
            },
            {
                "fieldname": "item_groups_section_break",
                "fieldtype": "Section Break",
                "insert_after": "targets",
                "label": "Item Groups",
            },
            {
                "fieldname": "item_groups",
                "fieldtype": "Table",
                "insert_after": "item_groups_section_break",
                "label": "Item Groups",
                "options": "Item Group Detail",
            },
        ],
        'Coupon Code': [
            {
                "fieldname": "ref_doctype",
                "fieldtype": "Link",
                "insert_after": "amended_from",
                "label": "Reference Type",
                "options": "DocType",
                "read_only": "1",
            },
            {
                "fieldname": "ref_docname",
                "fieldtype": "Dynamic Link",
                "insert_after": "ref_doctype",
                "label": "Reference Name",
                "options": "ref_doctype",
                "read_only": "1",
            }
        ],

        'Quotation': [
            {
                "fieldname": "sales_team_section_break",
                "fieldtype": "Section Break",
                "insert_after": "payment_schedule",
                "label": "Sales Team",
            },
            {
                "fieldname": "sales_team",
                "fieldtype": "Table",
                "insert_after": "sales_team_section_break",
                "label": "Sales Team",
                "options": "Sales Team"
            }
        ],
        'Selling Settings': [

            {
                "fieldname": "defatults_distributor_marketer_section_break",
                "fieldtype": "Section Break",
                "insert_after": "hide_tax_id",
                "label": "Distributor & Marketer",
            },
            {
                "fieldname": "default_distributer_territory",
                "fieldtype": "Link",
                "insert_after": "defatults_distributor_marketer_section_break",
                "label": "Default Distributor Territory",
                "options": "Territory"
            },
            {
                "fieldname": "default_distributer_customer_group",
                "fieldtype": "Link",
                "insert_after": "default_distributer_territory",
                "label": "Default Distributor Customer Group",
                "options": "Customer Group"
            },
            {
                "fieldname": "defatults_distributor_marketer_column_break",
                "fieldtype": "Column Break",
                "insert_after": "default_distributer_customer_group",
                "label": "",
            },
            {
                "fieldname": "default_marketer_territory",
                "fieldtype": "Link",
                "insert_after": "defatults_distributor_marketer_column_break",
                "label": "Default Marketer Territory",
                "options": "Territory"
            },
            {
                "fieldname": "default_marketer_customer_group",
                "fieldtype": "Link",
                "insert_after": "default_marketer_territory",
                "label": "Default Marketer Customer Group",
                "options": "Customer Group"
            }
        ],

        'E Commerce Settings': [
            {
                "fieldname": "default_customer_territory",
                "fieldtype": "Link",
                "insert_after": "default_customer_group",
                "label": "Default Customer Territory",
                "options": "Territory"
            }
        ],
        'Loyalty Program Collection': [
            {
                "fieldname": "return_collection_factor",
                "fieldtype": "Currency",
                "insert_after": "collection_factor",
                "label": "Return Collection Factor (=1 LP)",
                "reqd": "1",
                "in_list_view": "1",
                "columns": "3"
            }
        ],
        "Address": [
            {
                "fieldname": "building_no",
                "fieldtype": "Data",
                "insert_after": "tax_category",
                "label": "Building No",
                "reqd": 1
            },
            {
                "fieldname": "floor_no",
                "fieldtype": "Data",
                "insert_after": "building_no",
                "label": "Floor No",
                "reqd": 1
            },
            {
                "fieldname": "apartment_no",
                "fieldtype": "Data",
                "insert_after": "floor_no",
                "label": "Apartment No",
                "reqd": 1
            }
        ],
        "Sales Order": [
            {
                "fieldname": "note",
                "fieldtype": "Data",
                "insert_after": "territory",
                "label": "Note",
                "no_copy":1
            },
            {
                "fieldname": "is_synced",
                "fieldtype": "Check",
                "insert_after": "note",
                "label": "Is Synced",
                "hidden": 1,
                "no_copy":1
            },
            {
                "fieldname": "shipping_company",
                "fieldtype": "Select",
                "insert_after": "order_type",
                "label": "Shipping company",
                "read_only": 1,
                "options" : "\nflextock\njandt",
                "no_copy":1
            },
            {
                "fieldname"   : "total_weight",
                "fieldtype"   : "Data",
                "insert_after": "shipping_address",
                "label"       : "Total Weight",
                "read_only"   : 0,
                "default"     : 100,
                "no_copy"     :1
            },
            {
                "fieldname"   : "rtx_number",
                "fieldtype"   : "Data",
                "insert_after": "total_weight",
                "label"       : "RTX Serial",
                "read_only"   : 1,
                "no_copy"     :1
            }


        ]
    },
    "properties": [
        {
            "doctype": "Customer",
            "doctype_or_field": "DocField",
            "fieldname": "customer_type",
            "property": "options",
            "property_type": "Text",
            "value": "\nCompany\nIndividual\nMarketer\nDistributor"
        }
    ],
    "property_setters": [

    ],
    'on_setup': 'dynamic.elevana.setup.install_elevana'
}
