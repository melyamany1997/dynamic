#validate backed item with 

# 1 - git stock item 
# 2 git single bundle Item 
# 3- git complicated pundel from invocie items 



#solution

# 1 - create child table in sales invoice to set complicated pundel to clear the data 
# doc Tybe name Compicated Pundel 
# fields  = ["Parent Item" , -- > to git parent pundel 
#           "Item Code" , -- > to git current bundel item code 
#            "Item Group" , -- > to br ablicable for commetion template 
#            "From Warehouse" ,  -- > to set the child paked list template 
#            "Qty"  , 
#            "Actual Qty" , -- > add this field if we need it 
#            "Picked Qty" , --> if we need to set 
#               ]

from itertools import product
import frappe 
from frappe import _

def get_product_bundle_items(item_code):
	product_bundle = frappe.qb.DocType("Product Bundle")
	product_bundle_item = frappe.qb.DocType("Product Bundle Item")

	query = (
		frappe.qb.from_(product_bundle_item)
		.join(product_bundle)
		.on(product_bundle_item.parent == product_bundle.name)
		.select(
			product_bundle_item.item_code,
			product_bundle_item.qty,
			product_bundle_item.uom,
			product_bundle_item.description,
		)
		.where(product_bundle.new_item_code == item_code)
		.orderby(product_bundle_item.idx)
	)
	return query.run(as_dict=True)
#ckeck if item is pundel and is complicated 

#check if complicated
def is_product_bundle(item_code) :
	return bool(frappe.db.exists("Product Bundle", {"new_item_code": item_code}))

@frappe.whitelist()
def set_complicated_pundel_list(invoice):
  
    #clear invocie compicated_pund
    paked_list_len = 0
    cont = 0 
    invoice.set("compicated_pundel" , [])
    complicated_pundel = []
    pundels_list = []
    
    packe_list = [{i.parent_item :i.item_code } for i in invoice.packed_items]
    for item in invoice.items :
        # first levele item or bundel 
        
        is_pundel =  bool(frappe.db.exists("Product Bundle", {"new_item_code": item.item_code}))
        if is_pundel :
            #if item is first level pundel get pundel items as items
            
            items = get_product_bundle_items(item.item_code)
            parent_items = len(items)
            #item_obj = {item.item_code : parent_items}
            com_pundel_items = []
            for i in items :
            
                 
                # check second levele bundel 
                com_pundel = bool(frappe.db.exists("Product Bundle", {"new_item_code": i.item_code}))
                # add item to new Child table 
                #  
                # 
                if not com_pundel :
                    if {item.item_code :i.item_code }not in packe_list :
                        frappe.throw(f" parent {i.parent_item } with,{i.item_code} not  in packed list ")
                    cont += 1 
                if  com_pundel :
                    cont -=1
                    #remove item from parent packed list 
                    parent_items = parent_items -1
                    pundel_data = get_product_bundle_items(i.item_code)
                    com_pundel_items = []
                    for it in pundel_data :
                        #check if bundel is three level pundel  
                        if bool(frappe.db.exists("Product Bundle", {"new_item_code": it.item_code})) :
                            frappe.throw(f"""_( Parent item {pundel_data} Product Pundel {it.item_code})  Has three level of pundels And max level is Tow""")
                        cont += 1
                        #add second level bundel to packed list 
                       
                        if {item.item_code:it.item_code} not in packe_list  :
                            frappe.throw(f"Parent {item.item_code} item {it.item_code} not in packed list ")
                    pundels_list.append({i.item_code : len(pundel_data)})
                    com_pundel_items.append(i)
                    pi_row =invoice.append("compicated_pundel", {})
                    pi_row.parent_item = item.item_code
                    pi_row.item_code = i.item_code
                    pi_row.qty = i.qty * item.qty
                    pi_row.from_warehouse = item.warehouse
                    pi_row.picked_qty = len(pundel_data) 
                #pi_row.item_group = it.item_group
            item_obj = {item.item_code : parent_items}
            pundels_list.append(item_obj)
            complicated_pundel.append({item.item_code : com_pundel_items})
    total_amount =  0
    for i in pundels_list :
        for k,v in i.items() :
            total_amount +=v

    if len(packe_list) !=  total_amount :
        frappe.throw("Packing list error")
    frappe.msgprint("Packed Item Count is " + str(total_amount))

           