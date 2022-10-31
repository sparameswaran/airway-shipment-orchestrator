import json
import boto3
import os
import uuid

SHIPMENT_HASH_TABLE = os.getenv('SHIPMENT_HASH_TABLE')
SHIPMENT_RECORD_TABLE = os.getenv('SHIPMENT_RECORD_TABLE')
INVALID_SHIPMENT_RECORD_TABLE = os.getenv('INVALID_SHIPMENT_RECORD_TABLE')
AIRWAYS_SHIPMENT_TABLE = os.getenv('AIRWAYS_SHIPMENT_TABLE')

dynamodb = boto3.resource('dynamodb')


def recreateTable(tableName, partitionKey, sortKey):
    print('Starting recreation of Table: ', tableName)

    table = dynamodb.Table(tableName)

    try:
        table.delete()
        print('Deleting Table {}...', format(table.name))
        table.wait_until_not_exists()
    except Exception as inst:
        print('Table does not exist!!')

    keySchema = [ {'AttributeName': partitionKey, 'KeyType': 'HASH'} ]
    attributeDefinitions = [ {'AttributeName': partitionKey, 'AttributeType': 'S'} ]


    if sortKey is not None:
        keySchema.append({'AttributeName': sortKey, 'KeyType': 'RANGE'})
        attributeDefinitions.append({'AttributeName': sortKey, 'AttributeType': 'S'})

    # Not using provisioned throughput
    """"
    provisionedThroughput = {
                                'ReadCapacityUnits': 100,
                                'WriteCapacityUnits': 200
                            }
    """

    table = dynamodb.create_table(TableName=tableName,
                                    KeySchema=keySchema,
                                    AttributeDefinitions=attributeDefinitions,
                                    BillingMode='PAY_PER_REQUEST')
                                    #ProvisionedThroughput=provisionedThroughput)

    print('Creating Table {}...', format(tableName))
    table.wait_until_exists()


def deleteTableContent(tableName, partitionKey):
    print('Starting deletion of contents from Table: ', tableName)

    recordTable = dynamodb.Table(tableName)
    partitionKeyResponse = recordTable.scan( ProjectionExpression=partitionKey)

    totalRows = 0
    hashKeyEntries = partitionKeyResponse['Items']
    currentItems = len(partitionKeyResponse['Items'])

    while ( True ):

        counter = 0
        processed = 0
        batchWritePayload = []

        if len(hashKeyEntries) == 1:
            hashKeyEntry = hashKeyEntries[0]
            if not bool(hashKeyEntry):
                break

        for hashKeyEntry in hashKeyEntries:

            hashKey = hashKeyEntry[partitionKey]

            if (counter > 20):
                bulkDeleteRequest = { tableName: batchWritePayload }
                request = { "RequestItems": bulkDeleteRequest }
                #print('Bulk Delete request for records: ', bulkDeleteRequest)
                response = dynamodb.batch_write_item(RequestItems=bulkDeleteRequest)
                #print('Response:', response)
                totalRows += counter
                batchWritePayload = []
                counter = 0
            else:
                counter += 1

                entry = {
                            "DeleteRequest": {
                                "Key": {
                                    partitionKey :  hashKey
                                }
                            }
                        }

                batchWritePayload.append(entry)
                processed += 1

        # If we have finished the looping but something still left
        if len(batchWritePayload) > 0:
            bulkDeleteRequest = { tableName: batchWritePayload }
            request = { "RequestItems": bulkDeleteRequest }
            #print('Pending Bulk Delete request for records: ', bulkDeleteRequest)
            response = dynamodb.batch_write_item(RequestItems=bulkDeleteRequest)
            #print('Response:', response)

        print('Deleted {} entries from {}'.format(str(totalRows), tableName))
        # What if there are things still to be paged?
        if partitionKeyResponse.get('LastEvaluatedKey') is not None:
            print('More paginated rows left in {}!!'.format(tableName))
            newItemsResponse = recordTable.scan( ProjectionExpression=partitionKey)
            partitionKeyResponse = newItemsResponse
        else:
            break

    print('Finally deleted {} entries from {}\n'.format(str(totalRows), tableName))

def deleteTableContentWithSortKey(tableName, partitionKey, projectionSortKey):
    print('Starting deletion of contents from Table: {} with hash key: {} and sort key: {}'.format(tableName, partitionKey, projectionSortKey))

    recordTable = dynamodb.Table(tableName)
    partitionKeyResponse = recordTable.scan( ProjectionExpression=partitionKey)
    print(partitionKeyResponse)

    for hashKeyEntry in partitionKeyResponse['Items']:
        hashKey = hashKeyEntry[partitionKey]
        print("Handling Hash:", hashKey)
        itemsResponse = recordTable.query(
                ProjectionExpression=projectionSortKey,
                KeyConditionExpression = partitionKey + ' = :hash',
                ExpressionAttributeValues={ ':hash' : hashKey }
            )


        totalRows = 0

        while (len(itemsResponse['Items']) > 0 ):
            batchWritePayload = []
            counter = 0
            processed = 0
            currentItems = len(itemsResponse['Items'])
            totalRows += currentItems

            # Handle empty Items that show up as Items: [{}]
            if currentItems == 1:
                recordIdEntry = itemsResponse['Items'][0]
                if not bool(recordIdEntry):
                    break

            for recordIdEntry in itemsResponse['Items']:
                #print('RecordEntry ', recordIdEntry)

                if (counter > 20):
                    bulkDeleteRequest = { tableName: batchWritePayload }
                    request = { "RequestItems": bulkDeleteRequest }
                    #print('Bulk Delete request for records: ', bulkDeleteRequest)
                    response = dynamodb.batch_write_item(RequestItems=bulkDeleteRequest)
                    #print('Response:', response)
                    batchWritePayload = []
                    counter = 0
                else:
                    counter += 1

                entry = {
                            "DeleteRequest": {
                                "Key": {
                                    partitionKey :  hashKey,
                                    projectionSortKey: recordIdEntry[projectionSortKey]
                                }
                            }
                        }

                batchWritePayload.append(entry)
                processed += 1

            # If we have finished the looping but something still left
            if len(batchWritePayload) > 0:
                bulkDeleteRequest = { tableName: batchWritePayload }
                request = { "RequestItems": bulkDeleteRequest }
                #print('Bulk Delete request for records: ', bulkDeleteRequest)
                response = dynamodb.batch_write_item(RequestItems=bulkDeleteRequest)
                #print('Response:', response)

            print('Deleted {} entries from {}'.format(str(currentItems), tableName))
            # What if there are things still to be paged?
            if itemsResponse.get('LastEvaluatedKey') is not None:
                print('More paginated rows left in {}!!'.format(tableName))
                newItemsResponse = recordTable.query(
                    ProjectionExpression=projectionSortKey,
                    KeyConditionExpression= partitionKey + ' = :hash',
                    ExclusiveStartKey=itemsResponse.get('LastEvaluatedKey'),
                    ExpressionAttributeValues={ ':hash' : hashKey }
                )
                itemsResponse = newItemsResponse

            print('Finished deleting total of {} rows in {}\n'.format(str(totalRows), tableName))


def lambda_handler(event, context):
    """
    print('Deleting Table contents for Airways Shipping')
    deleteTableContent(AIRWAYS_SHIPMENT_TABLE, 'shipmentRecordID')

    # Faster to recreate ShipmentRecord Table
    recreateTable(SHIPMENT_RECORD_TABLE, 'addrDateHash', 'recordId')
    #deleteTableContentWithSortKey(SHIPMENT_RECORD_TABLE, 'addrDateHash', 'recordId')

    deleteTableContentWithSortKey(SHIPMENT_HASH_TABLE, 'addrHashCode', 'addrDateHash')
    """

    print('Deleting all tables and recreating them!!')

    # Faster to recreate Tables with on-demand capacity
    recreateTable(AIRWAYS_SHIPMENT_TABLE, 'shipmentRecordID', None)
    recreateTable(SHIPMENT_RECORD_TABLE, 'addrDateHash', 'recordId')
    recreateTable(INVALID_SHIPMENT_RECORD_TABLE, 'addrDateHash', 'recordId')
    recreateTable(SHIPMENT_HASH_TABLE, 'addrHashCode', 'addrDateHash')



"""
def lambda_handler(event, context):
    deleteTableContent(SHIPMENT_HASH_TABLE, 'addrHashCode', 'recordId', '')
    print('Incoming event: ', event)

    tableName = SHIPMENT_HASH_TABLE
    table = dynamodb.Table(tableName)
    hashIdsResponse = table.scan( ProjectionExpression="addrHashCode")
    print(hashIdsResponse)

    for addrHashEntry in hashIdsResponse['Items']:
        print("Handling Hash:", addrHashEntry)
        shipmentRecordtable = dynamodb.Table(SHIPMENT_RECORD_TABLE)
        shipmentIdsResponse = shipmentRecordtable.query(
                ProjectionExpression="recordId",
                KeyConditionExpression="addrHashCode = :hash",
                ExpressionAttributeValues={ ':hash' : addrHashEntry['addrHashCode'] }
            )

        totalRows = 0

        while (len(shipmentIdsResponse['Items']) > 0 ):
            batchWritePayload = []
            counter = 0
            processed = 0
            currentItems = len(shipmentIdsResponse['Items'])
            totalRows += currentItems

            for recordIdEntry in shipmentIdsResponse['Items']:

                if (counter > 20):
                    bulkDeleteRequest = { SHIPMENT_RECORD_TABLE: batchWritePayload }
                    request = { "RequestItems": bulkDeleteRequest }
                    print('Bulk Delete request for shipment records: ', bulkDeleteRequest)
                    response = dynamodb.batch_write_item(RequestItems=bulkDeleteRequest)
                    print('Response:', response)
                    batchWritePayload = []
                    counter = 0
                else:
                    counter += 1

                # entry = { "DeleteRequest":
                #             {
                #                 "Key":
                #                 {
                #                     "addrHashCode" : {
                #                         'S': addrHashEntry['addrHashCode']
                #                     },
                #                     "recordId": {
                #                         'S': recordIdEntry['recordId']
                #                     }
                #                 }
                #             }
                #         }
                entry = {
                            "DeleteRequest": {
                                "Key": {
                                    "addrHashCode" :  addrHashEntry['addrHashCode'],
                                    "recordId": recordIdEntry['recordId']
                                }
                            }
                        }

                batchWritePayload.append(entry)
                processed += 1

            # If we have finished the looping but something still left
            if len(batchWritePayload) > 0:
                bulkDeleteRequest = { SHIPMENT_RECORD_TABLE: batchWritePayload }
                request = { "RequestItems": bulkDeleteRequest }
                print('Bulk Delete request for shipment records: ', bulkDeleteRequest)
                response = dynamodb.batch_write_item(RequestItems=bulkDeleteRequest)
                print('Response:', response)

            print('Deleted {} entries from {}'.format(str(currentItems), SHIPMENT_RECORD_TABLE))
            # What if there are things still to be paged?
            if shipmentIdsResponse.get('LastEvaluatedKey') is not None:
                print('More paginated rows left in {}'.format(SHIPMENT_RECORD_TABLE))
                shipmentIdsResponse = shipmentRecordtable.query(
                    ProjectionExpression="recordId",
                    KeyConditionExpression="addrHashCode = :hash",
                    ExclusiveStartKey=shipmentIdsResponse.get('LastEvaluatedKey'),
                    ExpressionAttributeValues={ ':hash' : addrHashEntry['addrHashCode'] }
                )

            print('Finished deleting total of {} rows in {}'.format(str(totalRows), SHIPMENT_RECORD_TABLE))

"""
