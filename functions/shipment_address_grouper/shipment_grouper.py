import json
import boto3
import os
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.conditions import Attr

client = boto3.client('dynamodb')
SHIPMENT_HASH_TABLE = os.getenv('SHIPMENT_HASH_TABLE')

def lambda_handler(event, context):
    tableName=SHIPMENT_HASH_TABLE

    """
    response = client.scan(
        TableName='ShipmentHash',
        ProjectionExpression='addrHashCode',
        ExpressionAttributeValues={ ':wasProcessed' : { "BOOL": False } },
        FilterExpression='wasProcessed = :wasProcessed'
    )
    print(response)
    """

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(tableName)
    hashIdsResponse = table.scan(
        ProjectionExpression='addrHashCode',
        ExpressionAttributeValues={ ':wasProcessed' : False },
        FilterExpression='wasProcessed = :wasProcessed'
    )
    print(hashIdsResponse)

    return hashIdsResponse['Items']
