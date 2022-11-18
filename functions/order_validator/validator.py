import json
import boto3
import hashlib
import io
import os
from datetime import date
import random
import time

client = boto3.client('stepfunctions')
#stateMachineArn = os.getenv('BUSINESS_VALIDATION_STEPFUNCTION')
stateMachineArn = os.getenv('AIRWAYS_SHIPMENT_WORKFLOW_STEPFUNCTION')
MAX_PARTITION_RANGE = int(os.getenv('MAX_PARTITION_RANGE', 10))

def lambda_handler(event, context):
    print('Incoming Event with number of records: ', len(event['Records']))

    length = len(event['Records'])
    errors = {}
    response = { }

    for record in event['Records']:
        rawBody = record['body']
        #print('Shipment record:' , record['body'])
        ediRecord = json.loads(rawBody)

        # Go for the very first interchanges record
        ediRecord = ediRecord['interchanges'][0]

        addrHashMap = calculateHash(ediRecord)

        grpIndex = 0
        transactionSetIndex = 0
        addrSectionIndex = 0
        errors = []
        hasErrors = False

        for group in ediRecord['groups']:
            for transactionSet in group['transaction_sets']:
                for name_N1_loop_entry in  transactionSet['heading']['name_N1_loop']:
                    addrSection = name_N1_loop_entry['geographic_location_N4']
                    """
                    validationError = validateAddrRecord(addrSection)
                    #print("Addr Section: ", addrSection)
                    #print("Err?: ", validationError)
                    if validationError:
                        errorEntry = { 'message': validationError['message'], 'code': validationError['code'] }
                        path = [ "interchanges", "0", "groups", str(grpIndex), "transaction_sets", str(transactionSetIndex), "heading", "name_N1_loop", str(addrSectionIndex), validationError['field']   ]
                        errorEntry['path'] = path
                        errors.append(errorEntry)
                        #print('Errors: ', errors)
                    """

                    addrSectionIndex+=1
                transactionSetIndex+=1
            grpIndex+=1

        #addrSection = ediRecord['groups'][0]['transaction_sets'][0]['name_N1_loop']['geographic_location_N4']

        if 'FAIL' in rawBody.upper():
            errors.append( { 'code': 'max_length_exceeded', 'message': 'Test Error!! Value length must not exceed 2 for element N4-02', 'field': 'state_or_province_code_02' } )
            hasErrors = True
            ediRecord['errors'] = errors

        ediRecord['addrHash'] = addrHashMap
        ediRecord['recordId'] = record['messageId']

        inputPayload = { 'input': ediRecord }

        response = client.start_execution(
            stateMachineArn=stateMachineArn,
            input= json.dumps(inputPayload)
        )
        if hasErrors:
            print('Fired off step function for Business validation with failure scenario: {}'.format( response['executionArn']))


    return {
        'statusCode': 200,
        'body': json.dumps('Processed business validation rules against messages from Lambda!')
    }


def validateAddrRecord(georecord):
    print('Calling validate on ', georecord)
    state_code = georecord.get('state_or_province_code_02')
    postal_code = georecord.get('postal_code_03')
    country_code = georecord.get('country_code_04')
    if state_code is None:
        return { 'code': 'missing field', 'message': 'Value missing for element N4-02', 'field': 'state_or_province_code_02' }
    if len(state_code) > 2:
        return { 'code': 'max_length_exceeded', 'message': 'Value length must not exceed 2 for element N4-02', 'field': 'state_or_province_code_02' }

    if postal_code is None:
        return { 'code': 'missing field', 'message': 'Value missing for element N4-03', 'field': 'postal_code_03' }
    if len(postal_code) > 6:
        return { 'code': 'max_length_exceeded', 'message': 'Value length must not exceed 6 for element N4-03', 'field': 'postal_code_03' }

    if country_code is None:
        return { 'code': 'missing field', 'message': 'Value missing for element N4-04', 'field': 'country_code_04' }
    if len(country_code) > 3:
        return { 'code': 'max_length_exceeded', 'message': 'Value length must not exceed 6 for element N4-03', 'field': 'country_code_04' }

    return None


def calculateHash(ediRecord):

    addrString = ''
    grpIndex = 0
    for group in ediRecord['groups']:
        transactionSetIndex = 0
        for transactionSet in group['transaction_sets']:
            for name_N1_loop_entry in  transactionSet['heading']['name_N1_loop']:
                addrSectionIndex = 0
                if addrSectionIndex == 1 and name_N1_loop_entry.get('address_information_N3'):
                    for name_n3 in name_N1_loop_entry['address_information_N3']:
                        buf = io.StringIO()
                        buf.write('%s:%s' % (addrString, name_n3['address_information_01']))
                        addrString = buf.getvalue()

                addrSection = name_N1_loop_entry['geographic_location_N4']
                buf = io.StringIO()
                buf.write('%s:%s:%s:%s' % (addrString,
                                            addrSection.get('city_name_01'),
                                            addrSection.get('postal_code_03'),
                                            addrSection.get('country_code_04') ) )
                addrString = buf.getvalue()
                addrSectionIndex+=1

            transactionSetIndex+=1
        grpIndex+=1

    #addrSection = ediRecord['groups'][0]['transaction_sets'][0]['name_N1_loop']['geographic_location_N4']

    addrEncoded = addrString.encode()
    hashcode = hashlib.md5(addrEncoded).hexdigest()
    # Create hash with day and hour and minute so it shows up as brand new row in ShipmentHash and ShipmentRecord
    # Rather than overwriting existing records
    addrDateHash = hashcode + '#' + time.strftime("%Y-%m-%d-%H-%M") + '#' + str(random.randrange(MAX_PARTITION_RANGE))

    return { 'addrHashCode': hashcode, 'addrCombo' : addrString, 'addrDateHash': addrDateHash }
