import frappe

@frappe.whitelist()
def create_contract_service_item():
    try:
        item = frappe.new_doc("Item")
        item.item_code = "Contract"
        item.item_name = "Contract"
        item.description = "Contract"
        item.item_group = "Services"
        item.is_stock_item = False
        item.save()
    except:
        pass