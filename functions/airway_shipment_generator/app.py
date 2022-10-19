import json
import boto3
import os
import uuid
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.conditions import Attr

client = boto3.client('dynamodb')
SHIPMENT_RECORD_TABLE = os.getenv('SHIPMENT_RECORD_TABLE')

def lambda_handler(event, context):
    print('Incoming event: ', event)

    tableName = SHIPMENT_RECORD_TABLE
    hashKey = event['addrHashCode']
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(tableName)
    hashIdsResponse = table.query(
        KeyConditionExpression="addrHashCode = :hash",
        ExpressionAttributeValues={ ':hash' : hashKey }

    )
    print(hashIdsResponse)

    airwaybillJson = {
                	"sawb_bill_number": "933-13232-20239239",
                	"shipper": {
                		"name": "ABC Co Ltd",
                		"address": "3-2-1 Test Addr, San Francisco, State, USA"
                	},
                	"shipper_account_number": "23023320",
                	"airTransportAssoc": "NCA",
                	"issuedBy": {
                		"name": "UPS",
                		"address": "2332, Test addr, Lewisville, USA"
                	},

                	"consignee": {
                		"name": "ABC Company Branch",
                		"address": "Test Branch Location, Los Angeles, CA, USA"
                	},
                	"consignee_account_number": "232239320203",
                	"issuing_carrier": {
                		"name": "ABC Company Branch",
                		"address": "Test issuer Location, Irvine, CA, USA"
                	},

                	"agent_iata_code": "asl2423",
                	"agent_account_no": "23402423asfdas",
                	"airport_departure": "SFO",
                	"airport_to": "LAX",
                	"carrier": "UA2323",
                	"destination_airport": "LAX",
                	"accounting_information": "Test account details",
                	"reference_number": "2392asdfaf",
                	"optional_shipping_information": "",
                	"currency": "USD",
                	"declared_value_for_carriage": "$1000",
                	"declared_value_for_customs": "$1000",
                	"amt_of_insurance": "$1500"
                }

    airwaybillJson['shipment_entries'] = hashIdsResponse['Items']
    airwaybillJson['sawb_bill_number'] = str(uuid.uuid4())

    return airwaybillJson
