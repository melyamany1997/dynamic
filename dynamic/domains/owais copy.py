



from __future__ import unicode_literals


data = {

    'custom_fields': {
    },
      "properties": [
        # Sales Invoice Item
        {
            "doctype": "Sales Invoice Item",
            "doctype_or_field": "DocField",
            "fieldname": "item_code",
            "property": "columns",
            "property_type": "Int",
            "value": "1"
        },
        {
            "doctype": "Sales Invoice Item",
            "doctype_or_field": "DocField",
            "fieldname": "uom",
            "property": "columns",
            "property_type": "Int",
            "value": "1"
        },
        {
            "doctype": "Sales Invoice Item",
            "doctype_or_field": "DocField",
            "fieldname": "qty",
            "property": "columns",
            "property_type": "Int",
            "value": "1"
        },
        {
            "doctype": "Sales Invoice Item",
            "doctype_or_field": "DocField",
            "fieldname": "rate",
            "property": "columns",
            "property_type": "Int",
            "value": "2"
        },
        {
            "doctype": "Sales Invoice Item",
            "doctype_or_field": "DocField",
            "fieldname": "cost_center",
            "property": "in_list_view",
            "property_type": "Check",
            "value": "1"
        },
        {
            "doctype": "Sales Invoice Item",
            "doctype_or_field": "DocField",
            "fieldname": "batch_no",
            "property": "in_list_view",
            "property_type": "Check",
            "value": "0"
        },
        {
            "doctype": "Sales Invoice Item",
            "doctype_or_field": "DocField",
            "fieldname": "serial_no",
            "property": "in_list_view",
            "property_type": "Check",
            "value": "0"
        },
        {
            "doctype": "Sales Invoice Item",
            "doctype_or_field": "DocField",
            "fieldname": "warehouse",
            "property": "in_list_view",
            "property_type": "Check",
            "value": "1"
        },
        {
        "doctype": "Sales Invoice Item",
        "doctype_or_field": "DocField",
        "fieldname": "actual_qty",
        "property": "in_list_view",
        "property_type": "Check",
        "value": "1",
        },
        {
        "doctype": "Sales Invoice Item",
        "doctype_or_field": "DocField",
        "fieldname": "actual_qty",
        "property": "width",
        "property_type": "Text",
        "value": "1",
        }, 
        # Sales order Item 
        {
            "doctype": "Sales Order Item",
            "doctype_or_field": "DocField",
            "fieldname": "item_code",
            "property": "columns",
            "property_type": "Int",
            "value": "1"
        },
        {
            "doctype": "Sales Order Item",
            "doctype_or_field": "DocField",
            "fieldname": "uom",
            "property": "columns",
            "property_type": "Int",
            "value": "1"
        },
        {
            "doctype": "Sales Order Item",
            "doctype_or_field": "DocField",
            "fieldname": "qty",
            "property": "columns",
            "property_type": "Int",
            "value": "1"
        },
        {
            "doctype": "Sales Order Item",
            "doctype_or_field": "DocField",
            "fieldname": "rate",
            "property": "columns",
            "property_type": "Int",
            "value": "2"
        },
        {
            "doctype": "Sales Order Item",
            "doctype_or_field": "DocField",
            "fieldname": "description",
            "property": "in_list_view",
            "property_type": "Check",
            "value": "0"
        },
        {
            "doctype": "Sales Order Item",
            "doctype_or_field": "DocField",
            "fieldname": "supplier",
            "property": "in_list_view",
            "property_type": "Check",
            "value": "0"
        },

        {
            "doctype": "Sales Order Item",
            "doctype_or_field": "DocField",
            "fieldname": "warehouse",
            "property": "in_list_view",
            "property_type": "Check",
            "value": "1"
        },
        {
        "doctype": "Sales Order Item",
        "doctype_or_field": "DocField",
        "fieldname": "actual_qty",
        "property": "in_list_view",
        "property_type": "Check",
        "value": "1",
        },
        {
        "doctype": "Sales Order Item",
        "doctype_or_field": "DocField",
        "fieldname": "actual_qty",
        "property": "columns",
        "property_type": "Int",
        "value": "1"
        }, 
    ],
  
    # 'on_setup': 'dynamic.owais.setup.setup_owais'
}