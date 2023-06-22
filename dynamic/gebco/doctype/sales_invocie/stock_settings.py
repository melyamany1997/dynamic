from email import message
from pickletools import read_uint1
import frappe
from frappe import _ 
from collections import Counter
from functools import reduce
from operator import add
#this fuction caculate all shoratge stock item and msg print all aitem with shorage amount to wharehousr 

# function tak items as list of dic
#  and wharehouse

def validate_sql(out) :
    if len(out) > 0 :
        return out[0].get("actual_qty")
    else: return 0 
def get_item_availabel_stock_with_warehouse(item ,warehouse) :
    main_item = frappe.get_doc("Item" , item[0])
    if main_item.is_stock_item == 1 and warehouse :
        actual_qty = frappe.db.sql(f"""SELECT actual_qty FROM`tabBin` WHERE 
                item_code ='{ item[0]}' and 
                warehouse='{warehouse}'""",as_dict = 1)
        avilable_qty = validate_sql(actual_qty)
        if avilable_qty :
            required_qty = float(item[1] or 0 )
            if float(avilable_qty)  >  required_qty :
                pass
            if float(avilable_qty) <  required_qty  :
                shortage =  required_qty - float(avilable_qty)
                return {str(item[0] ): shortage  }   
        else :
             return {str(item[0])  : item[1]  }
       
def get_sum_items(item):
    main_item = frappe.get_doc("Item" , item.get("item_code"))
    if main_item.is_stock_item == 1 and item.get('warehouse') :   
        return {item.get("item_code") : item.get("qty")  }
    if not main_item.is_stock_item and item.get("parent_item")  :
        #frappe.throw(f"""Item Code {item.get("item_code")} Is not Stock Item { item.get("qty")} """)   
        pass
def caculate_shortage_item(items , wharehouse,*args ,**kwargs ) :
    str_o  = "[Completed]"
    data =list(map(get_sum_items ,items))
    wharehouselist =list( map(lambda item: item.get('warehouse') , items))
    sum_dict = reduce(add, (map(Counter, data)))

    #frappe.throw(str(sum_dict))
    wharehouselist = wharehouselist[0 :(len(sum_dict.items()) -1)]
    pure_data = list(map(get_item_availabel_stock_with_warehouse ,sum_dict.items() ,wharehouselist))
    cleard_data = list(filter(None, pure_data))
    str_o = list(map(lambda v : "<tr>" + "<td>" +str(list(v.keys())[0])  + "</td>" + "<td>" +str(list(v.values())[0])  + "</td> </<tr>" , cleard_data))
    frappe.msgprint(str(str_o))
    return str_o 
