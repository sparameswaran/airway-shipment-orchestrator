import json
import boto3
import os

tableName = os.getenv('SHIPMENT_HASH_TABLE')
dynamodb = boto3.resource('dynamodb')

def findAddressPartitions(addrHashCode):
    table = dynamodb.Table(tableName)

    exprValue = { }
    filtrExpression='attribute_not_exists(sawbHash) '

    if addrHashCode is not None:
        exprValue[':addrHashCodeValue'] = addrHashCode
        filtrExpression = filtrExpression + ' and addrHashCode = :addrHashCodeValue'

    args = { 'FilterExpression': filtrExpression, 'ProjectionExpression': 'addrHashCode,addrDateHash' }
    if exprValue:
        args['ExpressionAttributeValues'] = exprValue

    #print('Incoming addrHashCode: {} and expValue: {} and filtrExpression: {}'.format(addrHashCode, exprValue, filtrExpression))
    hashIdsResponse = table.scan(**args)
    print(hashIdsResponse)
    return hashIdsResponse['Items']


def createUniqueList(givenList):
    uniqueList = []
    for addrDateHash in givenList:
        if addrDateHash not in uniqueList:
            uniqueList.append(addrDateHash)
    return uniqueList

def findAddressGroups(event, context):
    # Find all available unique addresses by their hash, dont search for specific one.
    # findAddressByDatePartitions would try to pull with a given addrHashCode
    #print('Incoming payload for findAddrByHash: ', event)
    addrHashCode=None #event.get('addrHashCode')
    addressPartitions = findAddressPartitions(addrHashCode)
    addressList = [d['addrHashCode'] for d in addressPartitions]

    return createUniqueList(addressList)

def findAddressByDatePartitions(event, context):
    #print('Incoming payload for findAddrByPartitions: ', event)
    addrHashCode=event.get('addrHashCode')
    addressPartitions = findAddressPartitions(addrHashCode)
    addressList = [d['addrDateHash'] for d in addressPartitions]

    return createUniqueList(addressList)
