import json
import boto3
import os

tableName = os.getenv('SHIPMENT_HASH_TABLE')
dynamodb = boto3.resource('dynamodb')

def findAddressPartitions(addrHashCode):

    records = []
    moreRows = True
    exclusiveStartKey = None
    table = dynamodb.Table(tableName)

    while (moreRows):
        exprValue = { }
        filtrExpression='attribute_not_exists(sawbHash) '

        if addrHashCode is not None:
            exprValue[':addrHashCodeValue'] = addrHashCode
            filtrExpression = filtrExpression + ' and addrHashCode = :addrHashCodeValue'

        args = { 'FilterExpression': filtrExpression, 'ProjectionExpression': 'addrHashCode,addrDateHash' }

        if exprValue:
            args['ExpressionAttributeValues'] = exprValue

        if exclusiveStartKey:
            args['ExclusiveStartKey'] = exclusiveStartKey

        hashIdsResponse = table.scan(**args)
        print(hashIdsResponse)
        for row in hashIdsResponse['Items']:
            records.append(row)

        exclusiveStartKey=hashIdsResponse.get('LastEvaluatedKey')
        if exclusiveStartKey is not None:
                print('More paginated rows left in {}!!'.format(tableName))
        else:
            moreRows = False
    return records


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
    addrHashCode=None
    addressPartitions = findAddressPartitions(addrHashCode)
    print('Address partitions:', addressPartitions)
    addressList = [d['addrHashCode'] for d in addressPartitions]

    return createUniqueList(addressList)

def findAddressByDatePartitions(event, context):
    #print('Incoming payload for findAddrByPartitions: ', event)
    addrHashCode=event.get('addrHashCode')
    addressPartitions = findAddressPartitions(addrHashCode)
    addressList = [d['addrDateHash'] for d in addressPartitions]

    return createUniqueList(addressList)
