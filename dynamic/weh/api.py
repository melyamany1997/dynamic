import frappe
import requests
import json
from frappe import _

# url : /api/method/dynamic.weh.api.create_customer


@frappe.whitelist()
def customer(*args, **kwargs):
    try :
        data = json.loads(frappe.request.data)
    except Exception as e :
        frappe.local.response['message'] = f"Error Accourd   {e}"
        frappe.local.response['http_status_code'] = 400 
        return
    # validaion
    if not data.get("customer_name"):
        frappe.local.response['message'] = "Customer name required"
        frappe.local.response['http_status_code'] = 400 
        return
    if not data.get("remote_id"):
        frappe.local.response['message'] = "remote id required"
        frappe.local.response['http_status_code'] = 400 
        return

    if not frappe.db.exists("Customer",{"remote_id":data.get("remote_id")}):
        customer = frappe.new_doc("Customer")
    if  frappe.db.exists("Customer",{"remote_id":data.get("remote_id")}):    
        customer = frappe.get_doc("Customer",{"remote_id":data.get("remote_id")})
    customer.customer_name = data.get("customer_name")
    customer.customer_group = "All Customer Groups"
    customer.territory = "All Territories"
    customer.remote_id = data.get("remote_id")
    try:
        customer.save()
        frappe.local.response['message'] = customer.name
        frappe.local.response['http_status_code'] = 200 
        return
    except Exception as ex:
        frappe.local.response['message'] = str(ex)
        frappe.local.response['http_status_code'] = 400 
        return


@frappe.whitelist()
def get_consumables():
    try :
        data = json.loads(frappe.request.data)
    except Exception as e :
        frappe.local.response['message'] = f"Error Accourd   {e}"
        frappe.local.response['http_status_code'] = 400 
        return
    # if not data.get("date"):
    #     frappe.local.response['message'] = "Customer name required"
    #     frappe.local.response['http_status_code'] = 400 
    #     return
    if not data.get("remote_id"):
        frappe.local.response['message'] = "remote id required"
        frappe.local.response['http_status_code'] = 400 
        return
    if not frappe.db.exists("Customer",{"remote_id":data.get("remote_id")}):
        frappe.local.response['message'] = "CUSTOMER NOT FOUND !"
        frappe.local.response['http_status_code'] = 400 
    # if  frappe.db.exists("Customer",{"remote_id":data.get("remote_id")}):    
    customer = frappe.get_doc("Customer",{"remote_id":data.get("remote_id")})

    d_sql = f""" select name from `tabDelivery Note` WHERE customer='{customer.name}' """
    if data.get("date") :
        date =  data.get("date")
        d_sql = d_sql +f"and posting_date =date('{date}')"
    try :
        delvery_note = frappe.db.sql(f""" 
        select item_name , qty , rate , price_list_rate ,base_amount as amount from `tabDelivery Note Item` WHERE parent in ({d_sql})
        """,as_dict=1)
        frappe.local.response['message'] =delvery_note
        frappe.local.response['http_status_code'] = 200
        # return delvery_note
    except Exception as E :
        frappe.local.response['message'] = f"ERROR ! {E}"
        frappe.local.response['http_status_code'] = 400


def get_sum_consumables():
    try :
        data = json.loads(frappe.request.data)
    except Exception as e :
        frappe.local.response['message'] = f"Error Accourd   {e}"
        frappe.local.response['http_status_code'] = 400 
        return
    # if not data.get("date"):
    #     frappe.local.response['message'] = "Customer name required"
    #     frappe.local.response['http_status_code'] = 400 
    #     return
    if not data.get("remote_id"):
        frappe.local.response['message'] = "remote id required"
        frappe.local.response['http_status_code'] = 400 
        return
    if not frappe.db.exists("Customer",{"remote_id":data.get("remote_id")}):
        frappe.local.response['message'] = "CUSTOMER NOT FOUND !"
        frappe.local.response['http_status_code'] = 400 
    # if  frappe.db.exists("Customer",{"remote_id":data.get("remote_id")}):    
    customer = frappe.get_doc("Customer",{"remote_id":data.get("remote_id")})

    d_sql = f""" select name from `tabDelivery Note` WHERE customer='{customer.name}' """
    if data.get("date") :
        date =  data.get("date")
        d_sql = d_sql +f"and posting_date =date('{date}')"
    try :
        delvery_note = frappe.db.sql(f""" 
        select SUM( base_amount) as amount from `tabDelivery Note Item` WHERE parent in ({d_sql})
        """,as_dict=1)
        frappe.local.response['message'] =delvery_note
        frappe.local.response['http_status_code'] = 200
        # return delvery_note
    except Exception as E :
        frappe.local.response['message'] = f"ERROR ! {E}"
        frappe.local.response['http_status_code'] = 400