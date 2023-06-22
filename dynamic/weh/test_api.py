import requests
import json
# cusromer create function 


def create_customer() :
    key = "0a14eba40712351"
    secret= "cd1f2c06b3c5f90"
    url   = "http://0.0.0.0:8000"
    method = "/api/method/dynamic.weh.api.customer"
    data = {
        "customer_name":"Baba henawy huh" ,
        "remote_id" :27
    }
    header ={    'Authorization': f"Token {key}:{secret}"}
    r = requests.get(f"{url}{method}" , headers=header , data = json.dumps(data))
    print(r.text)
# create_customer()


def get_con():
    key = "0a14eba40712351"
    secret= "cd1f2c06b3c5f90"
    url   = "http://0.0.0.0:8000"
    method = "/api/method/dynamic.weh.api.get_consumables"
    data = {
        "date":"2023-01-29" ,
        "remote_id" :27
    }
    header ={    'Authorization': f"Token {key}:{secret}"}
    r = requests.get(f"{url}{method}" , headers=header , data = json.dumps(data))
    print(r.text)


get_con()