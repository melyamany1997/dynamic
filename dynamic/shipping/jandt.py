import hashlib
import frappe
import hmac
import base64
import time
import requests
import json
import datetime
from frappe import _

def generate_signature_string(api_key, api_secret, nonce):
    # Concatenate API key, nonce, and API secret
    message = api_key + str(nonce) + api_secret

    # Hash the message using SHA-256
    signature = hashlib.sha256(message.encode()).hexdigest()

    return signature

# def create_hedare_digest(api_secret):


@frappe.whitelist()
def get_key_and_secret_and_urls():
    """
    Get the key and secret from the J and T Settings doctype
    Returns:
          obj: key and secret
    """
    jt_settings = frappe.get_single("J and T Settings")
    if jt_settings.get("api_account") and jt_settings.get("private_key"):
        return {
            "api_account": jt_settings.get("api_account"),
            "private_key": jt_settings.get("private_key"),
            "create_order": jt_settings.get("create_order"),
            "checking_order": jt_settings.get("checking_order"),
            "cancel_order": jt_settings.get("cancel_order"),
            "order_status_reurn": jt_settings.get("order_status_reurn"),
            "customer_number" : jt_settings.get("customer_number"),
            "hashed_password":jt_settings.get("hashed_password")
        }

@frappe.whitelist()
def create_oder(product):
    """
    Args:
        product:

    Returns:
        obj: order status
    """
    product = json.loads(product)
    settings = get_key_and_secret_and_urls()
    if settings.get("create_order"):
        url = settings.get("create_order")
        apiaccount = settings.get("api_account")
        private_key = settings.get("private_key")
        timestamp = str(int(time.time() * 1000))
        customer_number = settings.get("customer_number")
        hashed_password = settings.get("hashed_password")

        # send time
        now = datetime.datetime.now()
        datetime_str = now.strftime("%Y-%m-%d %H:%M:%S")

        # create Business parameter signature 
        business_parameter_signature = create_body_signature(customer_number,hashed_password,private_key)
        customer = frappe.get_doc("Customer", product.get("customer"))

        description = ""
        for item in product.get("items"):
            description += item.get("item_code")+"-"+str(item.get("qty")) + ";"
        description = description[:-1] + "\n" + "مستحضرات تجميل"
        error_log = frappe.new_doc("Error Log")
        error_log.error = description
        error_log.save()
        if customer.get("customer_primary_address") and customer.get("customer_primary_contact"):
            customer_address = frappe.get_doc("Address", customer.get("customer_primary_address"))
            cutomer_contact = frappe.get_doc("Contact", customer.get("customer_primary_contact"))
            # body data 

            body = {
                "customerCode": customer_number,
                "digest": business_parameter_signature,
                "network": " ",
                "txlogisticId": product.get("name"),
                "expressType": "EZ",
                "orderType": "1",
                "serviceType": "02",
                "deliveryType": "04",
                "payType": "PP_PM",
                "sendStartTime": datetime_str,
                "sendEndTime": datetime_str,
                "goodsType": "ITN6",
                "length": "0",
                "width": "0",
                "height": "0",
                "weight": 1,
                "totalQuantity": 1,
                "itemsValue": product.get("grant_total"),
                "priceCurrency": "EGP",
                "offerFee": "",
                "remark": description,
                "operateType": 1,
                "sender": {
                    "name": "Elevana Integrated Medical",
                    "company": "Elevana Integrated Medical",
                    "postCode": "",
                    "mailBox": "",
                    "mobile": "01019814367",
                    "phone": "",
                    "countryCode": "EG",
                    "prov": "القاهره",
                    "city": "القاهره",
                    "area": "النزهه",
                    "street": "٣١ شارع مصر للطيران",
                    "building": "-",
                    "floor": "-",
                    "flats": "-",
                    "longitude": "",
                    "latitude": ""
                },
                "receiver": {
                    "name": customer.get("customer_name"),
                    "company": customer.get("customer_name"),
                    "postCode": customer_address.get("postal_code") if customer_address.get("postal_code") else "",
                    "mailBox": customer_address.get("email_id") if  customer_address.get("email_id") else "",
                    "mobile": cutomer_contact.phone_nos[0].phone if len(cutomer_contact.phone_nos) > 0 else "",
                    "phone": cutomer_contact.phone_nos[1].phone if len(cutomer_contact.phone_nos) > 1 else "",
                    "countryCode": "EG",
                    "prov": customer_address.state,
                    "city": customer_address.city,
                    "area": customer_address.state,
                    "street": customer_address.address_line1 + customer_address.address_line2,
                    "building": customer_address.building_no,
                    "floor":customer_address.floor_no ,
                    "flats": customer_address.apartment_no,
                    "longitude": "",
                    "latitude": "",
                },
                "items": [{
                    "itemType": "ITN6",
                    "itemName": item.get("item_name"),
                    "chineseName": "",
                    "englishName": "",
                    "number": 1,
                    "itemValue": item.get("rate"),
                    "priceCurrency": "EGP",
                    "desc": item.get("description"),
                    "itemUrl": ""
                    } for item in product.get("items")
                ],
                "customsInfo": {
                    "count": "",
                    "unit": "",
                    "sourceArea": "",
                    "productRecordNo": "",
                    "goodPrepardNo": "",
                    "taxNo": "",
                    "hsCode": "",
                    "goodsCode": "",
                    "brand": "",
                    "specifications": "",
                    "manufacturer": "",
                    "cargoDeclaredValue": "",
                    "declaredValueDeclaredCurrency": "",
                    "customerFreight": ""
                }
                }

            print("body",body)
       
            # generate header signature 
            header_digest = create_header_signature(private_key,body)
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-Requested-With': 'XMLHttpRequest',
                'Digest': header_digest,
                'Timestamp': timestamp,
                'apiAccount': apiaccount,
            }
            payload = {"bizContent":json.dumps(body)}
            response = requests.post(url, headers=headers, data=payload)
            #print(response.text)
            #if response.text.
            r = json.loads(response.text)
            order_name = product.get("name")
            print(r)
            if r.get("code") == "1":
                sql = f"""
                    update `tabSales Order` set is_synced=1 , shipping_company = "jandt" where name = '{order_name}' 
                """
                frappe.db.sql(sql)
                frappe.db.commit()
            return r.get("msg")
        else:
            frappe.msgprint(_("Please enter customer address and contacts"))


def checking_order():
    """
     check if order is shipped or not
    """
    settings = get_key_and_secret_and_urls()
    if settings.get("checking_order"):
        url = settings.get("checking_order")
        api_key = settings.get("api_account")
        api_secret = settings.get("private_key")
        timestamp = str(int(time.time() * 1000))
        string_to_hash = f'POST:{url}:{timestamp}'
        hashed = hmac.new(api_secret.encode(), string_to_hash.encode(), hashlib.sha256).hexdigest()
        header_digest = f'{base64.b64encode(bytes.fromhex(hashed)).decode()}'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest',
            'Digest': header_digest,
            'Timestamp': timestamp,
            'apiAccount': api_key,
        }
        payload = {"bizContent":"{'command': 1, 'serialNumber': ['EGYUAT81235870018'], 'customerCode': 'J0086024138', 'digest': 'wapT8IYOjNeViOL5eZupEg=='}"}
        response = requests.post(url, headers=headers, data=payload)
        
    else:
        pass

@frappe.whitelist()
def cancel_order(order):
    order = json.loads(order)
    settings = get_key_and_secret_and_urls()
    if settings.get("cancel_order"):
        url = settings.get("cancel_order")
        apiaccount = settings.get("api_account")
        private_key = settings.get("private_key")
        timestamp = str(int(time.time() * 1000))
        customer_number = settings.get("customer_number")
        hashed_password = settings.get("hashed_password")

        # send time
        now = datetime.datetime.now()
        datetime_str = now.strftime("%Y-%m-%d %H:%M:%S")

        # create Business parameter signature 
        business_parameter_signature = create_body_signature(customer_number,hashed_password,private_key)

        body = {'txlogisticId': order.get("name"),'orderType': 1, 'reason': 'wrong data', 'customerCode': customer_number, 'digest': business_parameter_signature}
        # create header digest 
        header_digest = create_header_signature(private_key,body)
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest',
            'Digest': header_digest,
            'Timestamp': timestamp,
            'apiAccount': apiaccount,
        }
        payload = {"bizContent":json.dumps(body)}
        response = requests.post(url, headers=headers, data=payload)
        r = json.loads(response.text)
        return r.get("msg")
    else:
        pass


# def order_status_return(doc):
#     settings = get_key_and_secret_and_urls()
#     if settings.get("order_status_reurn"):
#         url = settings.get("order_status_reurn")
#     else:
#         pass





@frappe.whitelist()
def create_body_signature(customerCode,pwd,privatekey):
    """
    create body signature
    Args:
        customerCode:
        pwd:
        privatekey:

    Returns:
        signature_base64
    """
    to_sign = customerCode +  pwd + privatekey
    signature = hashlib.md5(to_sign.encode()).digest()
    signature_base64 = base64.b64encode(signature).decode()

    print("body_signature",signature_base64)
    return signature_base64


@frappe.whitelist()
def create_header_signature(privatekey ,bizContent):
    """
    create header signature
    Args:
        privatekey:  private key
        bizContent: dict

    Returns:
        signature_base64
    """
    to_sign = json.dumps(bizContent) +  str(privatekey)
    signature = hashlib.md5(to_sign.encode()).digest()
    signature_base64 = base64.b64encode(signature).decode()
    print("header_signature",signature_base64)
    return signature_base64
    
@frappe.whitelist()
def create_password():
    """
    create password
    Returns:
    """
    customer_number = "J0086002753"
    plain_text_password = "P4dhv2D1"
    private_key = "a0a1047cce70493c9d5d29704f05d0d9"

    # Step 1
    plaintext = plain_text_password + "jadada236t2"
    # Step 2
    password_hash = hashlib.md5(plaintext.encode()).hexdigest()
    print(password_hash.upper())
    # Step 3
    # cipher_text = password_hash + "jadada236t2"
    # concatenated = cipher_text.encode()

    # # Step 4
    # to_sign = customer_number.encode() + concatenated + private_key.encode()

    # # Step 5
    # signature = hashlib.md5(to_sign).digest()
    # signature_base64 = base64.b64encode(signature).decode()

    # print(signature_base64)