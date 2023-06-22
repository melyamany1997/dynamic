import requests
import sys
import base64
import json

INSTANCE_URL = "https://api.maytapi.com/api"
PRODUCT_ID = "7e051015-df51-46d9-b585-3caa5265bf62"
API_TOKEN = "e08016cd-08a9-4250-a5b8-6c4cf2054001"
PHONE_ID = "23656"


def sendMessage():
    url = INSTANCE_URL + f"/{PRODUCT_ID}/{PHONE_ID}/sendMessage"
    payload = {

        "message" : "Hello From Other Side" ,
        # "text" : "hello user text" ,
        "to_number" : "00201205554644",
        "type": "text"

    }
    headers = {
        "Content-Type": "application/json",
        "x-maytapi-key": API_TOKEN,
    }
    r = requests.request('POST', url, headers=headers, data=json.dumps(payload))
    tjson = r.json()
    print(tjson)
    # pData = tjson["data"]
    # pSuccess = tjson["success"]
    # if pSuccess == True and len(pData) > 0:
    #     pId = tjson["data"][0]["productId"]
    #     return pId
    # else:
    #     return 0

sendMessage()