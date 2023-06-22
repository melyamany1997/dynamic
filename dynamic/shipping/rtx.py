import frappe
import json
import requests
from frappe import _
import datetime
from frappe.desk.form.load import get_attachments


def create_erro_log(source,e) :
   doc = frappe.new_doc("Error Log")
   doc.method = f"{source}"
   doc.error = f"{e}"
   doc.save()
   frappe.msgprint("Error created")
def validate_shipping_settings():
    """ validate shipping settings
    Returns:
        obj: shipping_settings
        """
    shipping_settings = frappe.get_single("RTX Settings")
    if shipping_settings.get("url") and shipping_settings.get("user_name") and shipping_settings.get(
            "password"):
        return {
            "status": True,
            "url": shipping_settings.get("url"),
            "user_name": shipping_settings.get("user_name"),
            "password": shipping_settings.get("password"),
            "wight" : shipping_settings.get("default_wight"),
            "content" :shipping_settings.get("default_content")
  

        }

    return {"status": False}
#dynamic.shipping.rtx
def get_token() :
   data = validate_shipping_settings()
   method_url = "/integration/token"
   url = f"{data.get('url')}{method_url}"
   data = {
       "username" : f"{data.get('user_name')}" ,
       "password" : f"{data.get('password')}"
   }
   header = {
      "Content-Type" :"application/json"
   }
   try :
      req = requests.post(url , data=json.dumps(data) ,headers=header)
      if req.status_code == 200 :
         token_data = req.json()
         print("Data token ++++++++++++" ,token_data.get("token"))
         return token_data.get("token")
      else :
         #create Erro Log
         create_erro_log("RTX login Error" , str(req.text))
         return False
   except Exception as e :
      create_erro_log("RTX login Error" , str(e))
      return False



@frappe.whitelist()
def create_oder(product):
   """
   dynamic.shipping.rtx.create_oder
   Args:
      product: product object
   Returns:
      listOfObjects : list<Object>

   required data : 
      full_name 
      phone
      notes
      order_date fromate 2022-11-09T02:00:00+02:00
      shipment_contents  
      weight
      city will not represent now 


   """
   method_url = "/integration/order"
   product = json.loads(product)
   data = validate_shipping_settings()
   url = f"{data.get('url')}{method_url}"
   now = datetime.datetime.now()
   datetime_str = now.strftime("%Y-%m-%d %H:%M:%S")
   customer = frappe.get_doc("Customer", product.get("customer"))
   if not customer :
      create_erro_log("RTX" , "Invalid Customer Data")
      frappe.throw("customer Error in RTX Create Order")
      return False
   address = ""
   cutomer_contact = ""
   customer_address = ""
   # check if address has phone number 
   if product.get("customer_address") :
      address_obj  = frappe.get_doc("Address" , product.get("customer_address"))
      address = address_obj.address_line1 or ""
      phone =  address_obj.phone or ""
   if customer.get("customer_primary_address") and customer.get("customer_primary_contact"):
      customer_address = frappe.get_doc("Address", customer.get("customer_primary_address"))
      cutomer_contact = frappe.get_doc("Contact", customer.get("customer_primary_contact"))
      if len(address) < 2 :
         address = customer_address.address_line1
      if len(phone) < 2 :
         phone = cutomer_contact.phone_nos[0].phone if len(cutomer_contact.phone_nos) > 0 else ""

   pay_load = {
      "full_name"         : customer.customer_name ,
      "phone"             : phone ,
      "notes"             : product.get("notes") or " " ,
      "order_date"        : datetime_str ,
      "shipment_contents" : data.get("content") ,
      "weight"            : data.get("wight")
   }
   token = get_token()
   print(token)
   if token :
      header = {
          "Content-Type" :"application/json" ,
          "Authorization" : f"Bearer {token}"
      }
      try :
         req = requests.post(url , data=json.dumps(pay_load) , headers=header)
         print(req.status_code)
         if req.status_code == 201 :
            respo = req.json()
            sql = f"""
                    update `tabSales Order` set is_synced=1 , rtx_number ="{respo.get('serial')}" where name='{product.get("name")}'
                """
            frappe.db.sql(sql)
            frappe.db.commit()
            frappe.msgprint("Order Sent to RTX")
            return 0
         else :
            create_erro_log("RTX Error" , req.text)
            frappe.msgprint("error Accourd")
            return 0

      except Exception as e :
         create_erro_log("RTX Error" , str(e))
         frappe.msgprint("error Accourd")
         return 0