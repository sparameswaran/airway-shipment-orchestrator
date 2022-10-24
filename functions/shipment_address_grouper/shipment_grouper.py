import json
import boto3
import os

tableName = os.getenv('SHIPMENT_HASH_TABLE')
dynamodb = boto3.resource('dynamodb')

def findAddressPartitions():
    table = dynamodb.Table(tableName)
    hashIdsResponse = table.scan(
        ProjectionExpression='addrHashCode,addrDateHash',
        ExpressionAttributeValues={ ':wasProcessed' : 'true' },
        FilterExpression='(wasProcessed <> :wasProcessed or attribute_not_exists(wasProcessed) ) and attribute_not_exists(sawbHash) '
    )
    print(hashIdsResponse)
    return hashIdsResponse['Items']

def createUniqueList(givenList):
    uniqueList = []
    for addrDateHash in givenList:
        if addrDateHash not in uniqueList:
            uniqueList.append(addrDateHash)
    return uniqueList

def findAddressGroups(event, context):
    addressPartitions = findAddressPartitions()
    addressList = [d['addrHashCode'] for d in addressPartitions]
    
    return createUniqueList(addressList)
    
def findAddressByDatePartitions(event, context):
    addressPartitions = findAddressPartitions()
    addressList = [d['addrDateHash'] for d in addressPartitions]
    
    return createUniqueList(addressList)
