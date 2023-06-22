import frappe
import json
import requests
from frappe import _

from frappe.desk.form.load import get_attachments


# 1. Authentication  URL: https://staging.flextock.com/base/auth/,

@frappe.whitelist()
def authenticate():
    """
       Authenticate Shipping Settings
         :return: access_token
    """
    try:
        method_url = "/base/auth/"
        data = validate_shipping_settings()
        if data.get("status"):
            base_url = data.get("url")
            body = {
                "username": data.get("user_name"),
                "password": data.get("password"),
                "key": data.get("key")
            }
            header = { "Content-Type" :"application/json",
            "Accept": "application/json",
            "Connection" :"keep-alive" ,
            "Accept-Encoding" :"gzip, deflate, br" ,
            "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36" }
         
            url = base_url + method_url
            r = requests.post(url, headers=header ,data=json.dumps(body))
            print(r.text)
            if r.status_code == 200:
                response = json.loads(r.text)
                access_token = response.get("access")
                # print("access_token",access_token)
                # frappe.set_value("Shipping Settings", "Shipping Settings", "token", access_token)
                return access_token
            else:
                frappe.log_error(
                    title=_("Error while shiiping authentications"),
                    message=r.text,
                )
        else:
            frappe.log_error(
                title=_("Error while shiiping authentications"),
                message="Error while shiiping authentications",
            )
    except Exception as ex:
        frappe.msgprint("failed to authente with flexstock")
        return


# 2. Create Product   ---> take list of product
@frappe.whitelist()
def create_product(product):
    product = json.loads(product)
    """
    Args:
        product: product object
    Returns:
        listOfObjects : list<Object>
    """
    data = validate_shipping_settings()
    if data.get("status"):
        method_url = "/external-integration/create-products/"
        base_url = data.get("url")
        url = base_url + method_url
        token = authenticate()
        # attachments = get_attachments("Item", product.name)
        # print("attachments", attachments)
        data = {
            "products": [
                {
                    "sku_code": product.get("item_code"),
                    "sku_name": product.get("item_name"),
                    "sku_description": product.get("item_name"),
                    "sku_image_url": "https://cdn.images.example/images/sku00111.jpg"
                }
            ]
        }
        print("token",token)
        if not token:
            frappe.throw("failed to authente with flexstock")
            return 
        headers = {
            "Authorization": f"""Bearer {token}"""
        }
        try:
            r = requests.post(url, headers=headers, json=data)
            res = json.loads(r.text)
        except Exception as e:
            frappe.msgprint(str(r.text))
        if r.status_code == 200:
            return res.get("response")[0].get("message")
        else:
            frappe.log_error(
                title=_("Error while create products"),
                message=r.text,
            )
        return res.get("response")[0].get("message")


# create order
@frappe.whitelist()
def create_order(doc, *args, **kwargs):
    """
    Args:
        doc: sales order
    Returns:
        listOfObjects : list<Object>
    """
    doc = json.loads(doc)

    data = validate_shipping_settings()
    if data.get("status"):
        method_url = "/external-integration/create-order/"
        base_url = data.get("url")
        url = base_url + method_url
        token = authenticate()
        customer = frappe.get_doc("Customer", doc.get("customer"))
        customer_name = customer.customer_name.split(" ")
        address_obj = {}
        if customer.get("customer_primary_address") and customer.get("customer_primary_contact"):
            customer_address = frappe.get_doc("Address", customer.get("customer_primary_address"))
            cutomer_contact = frappe.get_doc("Contact", customer.get("customer_primary_contact"))
            address_obj = {
                "city": customer_address.city,
                "area": customer_address.state,
                "address_line1": customer_address.address_line1,
                "address_line2": customer_address.address_line2,
                "building_no": customer_address.building_no,
                "floor_no": customer_address.floor_no,
                "apartment_no": customer_address.apartment_no,
                "is_work_address": False,
                "first_name": customer_name[0],
                "last_name": customer_name[1] if len(customer_name) > 1 else "",

                "phone_number": cutomer_contact.phone_nos[0].phone if len(cutomer_contact.phone_nos) > 0 else "",
                "secondary_phone_number": cutomer_contact.phone_nos[1].phone if len(
                    cutomer_contact.phone_nos) > 1 else "",
                "note": "note"
            }

        else:
            return "Customer address is missing"
        data = {
            "order_code": doc.get("name"),
            "order_date": doc.get("transaction_date"),
            "cash_on_delivery": doc.get("total"),
            "integration_source": "elevana",
            "customer_address": address_obj,
            "line_items": [
                {
                    "sku_code": item.get("item_code"),
                    "quantity": item.get("qty")
                } for item in doc.get("items")
            ]
        }

        headers = {
            "Authorization": f"""Bearer {token}"""
        }
        r = requests.post(url, headers=headers, json=data)
        print("rrr", r.text)
        res = json.loads(r.text)
        if r.status_code == 200:
            sql = f"""
                    update `tabSales Order` set is_synced=1 where name='{doc.get("name")}'
                """
            frappe.db.sql(sql)
            frappe.db.commit()
        else:
            frappe.log_error(
                title=_("Error while create order"),
                message=r.text,
            )
        return res.get("message")


# 4. Get Order status:
def get_order_status(order_code):
    """
    Args:
        order_code: order code
    Returns:
        obj: order status
    """
    data = validate_shipping_settings()
    if data.get("status"):
        method_url = "/order-status/"
        base_url = data.get("url")
        url = base_url + method_url
        token = authenticate()
        r = requests.post(url, data)
        if r.status_code == 200:
            return r.text
        else:
            frappe.log_error(
                title=_("Error while get order status"),
                message=r.text,
            )


def validate_shipping_settings():
    """ validate shipping settings
    Returns:
        obj: shipping_settings
        """
    shipping_settings = frappe.get_single("Shipping Settings")
    if shipping_settings.get("url") and shipping_settings.get("user_name") and shipping_settings.get(
            "password") and shipping_settings.get("key"):
        return {
            "status": True,
            "url": shipping_settings.get("url"),
            "user_name": shipping_settings.get("user_name"),
            "password": shipping_settings.get("password"),
            "key": shipping_settings.get("key")

        }

    return {"status": False}



