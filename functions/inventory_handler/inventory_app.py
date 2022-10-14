import json
import uuid

def lambda_handler(event, context):
    print('Incoming event: ', event)

    inventory = { "Inventory": { "available": 1000, "item_type": "test item order", "vendor_id": str(uuid.uuid4()) } }
    return inventory
