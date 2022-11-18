import json
import boto3
import os
from datetime import datetime

ACTIVE_TIME_WINDOW = os.getenv('ACTIVE_TIME_WINDOW_IN_MINUTES')
tableName = os.getenv('AIRWAYS_SHIPMENT_SHADOW_TABLE')
dynamodb = boto3.resource('dynamodb')

def findLatestAirwayShipment(event, context):

    addrHashCode = event.get('addrHashCode')
    print('Searching for addrHashCode prefix: ', addrHashCode)
    
    records = []
    moreRows = True
    exclusiveStartKey = None
    table = dynamodb.Table(tableName)

    exprValue = { }
    
    if addrHashCode is not None:
        exprValue[':addrDatePrefix'] = addrHashCode
        filterExpression = 'begins_with(addrDateHash, :addrDatePrefix)'

    args = {
            'ProjectionExpression': 'shipmentRecordID, addrDateHash, processDate, processTime',
            #'ScanIndexForward': False
    }

    if exprValue:
        args['ExpressionAttributeValues'] = exprValue
        args['FilterExpression'] = filterExpression

    shipmentRecordIdsResponse = table.scan(**args)
    print(shipmentRecordIdsResponse)
    for row in shipmentRecordIdsResponse['Items']:
        records.append(row)
    
    # Sort them by most recent
    newsortedRecords = sorted(records, key=lambda d: d['processTime'], reverse=True)
    
    # Check if we have atleast 1 record that matches the hash id.
    if len(newsortedRecords) > 0:
        processTime = newsortedRecords[0]['processTime']
        # Check if the last shipment bill was within ACTIVE_TIME_WINDOW minutes of current check.
        # if its over X minutes, then treat it as older batch and return empty.
        format='%Y-%m-%dT%H:%M:%S.%fZ'
        datetimeEntered = datetime.strptime(processTime, format)
        datetimeNow = datetime.now()
        delta = datetimeNow.timestamp() - datetimeEntered.timestamp()
        if (delta < (int(ACTIVE_TIME_WINDOW)*60)):
            return newsortedRecords[0]
            
    raise Exception('Record does not exist yet for matching airways shipment bill or need to kick off aggregation. Retry!!')

def createUniqueList(givenList):
    uniqueList = []
    for addrDateHash in givenList:
        if addrDateHash not in uniqueList:
            uniqueList.append(addrDateHash)
    return uniqueList
