import json
import os
import boto3

AIRWAYS_SHIPMENT_SHADOW_TABLE = os.getenv('AIRWAYS_SHIPMENT_SHADOW_TABLE')

dynamodb = boto3.resource('dynamodb')

def deleteTableContent(event, context):
    print('Starting deletion of contents from Table: ', AIRWAYS_SHIPMENT_SHADOW_TABLE)

    tableName = AIRWAYS_SHIPMENT_SHADOW_TABLE
    partitionKey = 'shipmentRecordID'
    
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

    return {
        'statusCode': 200,
        'body': json.dumps('Deleted contents from AirwaysShipmentDetailShadow table!!')
    }
