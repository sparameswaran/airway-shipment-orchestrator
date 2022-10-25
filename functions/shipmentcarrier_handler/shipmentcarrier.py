import json
import boto3
import os

client = boto3.client('stepfunctions')
stateMachineArn = os.getenv('SHIPMENT_TRANSPORTER_STEPFUNCTION')

def lambda_handler(event, context):
    print('Incoming Shipment Transport request with number of records: ', len(event['Records']))

    payload = {}
    messages = []
    payload['Length'] = len(event['Records'])

    for record in event['Records']:
        #print('Raw record:', record)
        
        """
        {'messageId': 'b88e9e89-2b0c-4aaa-ba4e-45742f821ece', 'receiptHandle': 'AQEBRJZYNwIjnCbOHEqUnBp56VDQDdYw/j3Q==',
        'body': '{\n  "Type" : "Notification",\n  "MessageId" : "ec19ec35-2f66-575a-ae00-b7faddbf9873",\n
            "TopicArn" : "arn:aws:sns:us-east-1:xxxx:ShipmentTransporterTopic",\n
            "Message" : "{\\n   \"Shipment\\": {\\n      \\"recordId\\": {\\n        \\"S\\": \\"ffa1a88b-d09b-4de0-a756-ce211776f227\\"\\n      },\\n
            \\"addrDateHash\\": {\\n        \\"S\\": \\"96d45cfc197a0588e8135a9c4ba85a18#2022-10-23#9\\"\\n      },\\n
            \\"processTime\\": {\\n        \\"S\\": \\"2022-10-23T07:12:53.001Z\\"\\n      }\\n    },\\n
            \\"AddressDateHash\\": \\"96d45cfc197a0588e8135a9c4ba85a18#2022-10-23#9\\",\\n
            \\"AddressHash\\": \\"8c728cce90f275158b21f455ac2cb357\\",\\n
            \\"AirwayBillNumber\\": \\"8c08ec5f-e65a-4a24-89a1-ddedb38e5878\\"\\n  }",\n
            "Timestamp" : "2022-10-24T01:55:37.261Z",\n  "SignatureVersion" : "1",\n
            "Signature" : "WGbVZdHOxo7hmpUaJTIwR/J+2TGcjzUfZ8f+r6k35JcdXhV9XJzLxQ==",\n
            "SigningCertURL" : "https://sns.us-east-1.amazonaws.com/SimpleNotificationService-56e67fcb41f6fec09b0196692625d385.pem",\n
            "UnsubscribeURL" : "https://sns.us-east-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:usTransporterTopic:f7ae82d2-a439-4efc-b970-b4133e4fdd14",\n
            "MessageAttributes" : {\n    "Carrier" : {"Type":"String","Value":"{       \\"DataType\\": \\"String\\",       \\"StringValue\\": \\"UPS\\"     }"}\n  }\n}',
            'attributes': {'ApproximateReceiveCount': '1', 'SentTimestamp': '1666576537301', 'SenderId': 'AIDAIT2UOQQY3AUEKVGXU', 'ApproximateFirstReceiveTimestamp': '1666576537311'},
            'messageAttributes': {}, 'md5OfBody': 'ba123a9c9249ffe49e7225d27098298f', 'eventSource': 'aws:sqs',
            'eventSourceARN': 'arn:aws:sqs:us-east-1:xxxx:ShipmentTransporterQueue', 'awsRegion': 'us-east-1'}
        """
        # Data from SNS - actual message payload is inside body --> message

        rawBody = record['body']
        jsonBody = json.loads(rawBody)
        actualMessage = jsonBody['Message']
        messageAttributes = jsonBody['MessageAttributes']

        # print('raw body: ', rawBody)        #
        # print('Message body: ', actualMessage)
        # print('Message attributes: ', messageAttributes)
        result = { 'Payload': json.loads(str(actualMessage)), 'MessageAttributes': messageAttributes }

        messages.append( result  )

    payload['Messages'] = messages
    #print('Final Payload: ', payload)
    response = client.start_execution(
        stateMachineArn=stateMachineArn,
        input=json.dumps(payload)
    )
    print('Fired off step functions for Shipment Transporter!!')
