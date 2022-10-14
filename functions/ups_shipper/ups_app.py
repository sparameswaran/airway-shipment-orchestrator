import json
import uuid

def lambda_handler(event, context):
    print('Incoming event: ', event)

    shipment =  {
        "description": "Shipment from  Zhengzhou",
        "shipper": {
          "name": "FoxConn",
          "attentionName": "John Doe",
          "phone": "12311",
          "shipperNumber": "A123B89",
          "phone": "1212311",
          "address": {
            "address1": "Flat 9999",
            "address2": "Sun West Center Mall",
            "address3": "25 West Yip Street",
            "city": "Zhengzhou",
            "state": "HK",
            "country": "CN",
            "zip": "723093",
          },
        },
        "shipTo": {
          "companyName": "Company Name",
          "attentionName": "Pedro Calunsod",
          "phone": "12321341",
          "address": {
            "address1": "999 Warrior St.",
            "address2": "Maria Cons. Subd. Shiper",
            "address3": "Stage, Valley",
            "city": "Louisville",
            "state": "KY",
            "country": "US",
            "zip": "40222",
          },
        },
        "payment": {
          "accountNumber": "A123B89",
        },
        "service": {
          "code": "expedited",
        },
        "package": [
          {
            "code": "02",
            "weight": "1",
          },
          {
            "code": "02",
            "weight": "1",
          },
        ],
        "shipment_code": str(uuid.uuid4()).
        "payload": event
      }


    return shipment
