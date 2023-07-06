from __future__ import unicode_literals

data = {
    'custom_fields': {
        'Sales Invoice': [
             {
                "fieldname": "compicated_pundel",
                "fieldtype": "Table",
                "options":"Compicated Pundel",
                "insert_after": "packing_list",
                "label": "Compicated Pundel",
                "read_only":1,
                
            },

        ],
        'Delivery Note':[
             {
                "fieldname": "compicated_pundel",
                "fieldtype": "Table",
                "options":"Compicated Pundel",
                "insert_after": "packing_list",
                "label": "Compicated Pundel",
                "read_only":1,
                
            },
        ],
        'Product Bundle': [
            {
                "fieldname": "item_name",
                "fieldtype": "Data",
                "insert_after": "new_item_code",
                "label": "Item Name",
                "read_only":1,
                "fetch_from":"new_item_code.item_name",
                "in_list_view":1
            },
            {
                "fieldname": "total_cost",
                "fieldtype": "Currency",
                "insert_after": "items",
                "label": "Total Cost",
                "default": "0",
                "read_only":1
            }
        ],
        'Product Bundle Item': [
            {
                "fieldname": "item_name",
                "fieldtype": "Data",
                "insert_after": "item_code",
                "label": "Item Name",
                "read_only":1,
                "fetch_from":"item_code.item_name",
                "in_list_view":1
            },
            {
                "fieldname": "cost",
                "fieldtype": "Currency",
                "insert_after": "qty",
                "label": "Cost",
                "default": "0",
                "read_only":1,
                "in_list_view":1
            },{
                "fieldname": "total_cost",
                "fieldtype": "Currency",
                "insert_after": "cost",
                "label": "Total Cost",
                "default": "0",
                "read_only":1,
                "in_list_view":1
            }
        ],
    },
    # "properties": [{
    #     "doctype":"Journal Entry Account",
    #     "doctype_or_field":"DocField",
    #     "fieldname":"reference_type",
    #     "property":"options",
    #     "property_type":"Text",
    #     "value": "\nSales Invoice\nPurchase Invoice\nJournal Entry\nSales Order\nPurchase Order\nExpense Claim\nAsset\nLoan\nPayroll Entry\nEmployee Advance\nExchange Rate Revaluation\nInvoice Discounting\nFees\nPay and Receipt Document\nComparison\nClearance\nTender"
    # }],
    'on_setup': 'dynamic.product_bundle.setup.install'
}
