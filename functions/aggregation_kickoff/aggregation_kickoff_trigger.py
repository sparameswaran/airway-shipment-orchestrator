import json
import boto3
import os


client = boto3.client('stepfunctions')
stateMachineArn = os.getenv('ORCHESTRATION_KICKOFF_STEPFUNCTION')

def lambda_handler(event, context):
    print('Incoming Event: ', event)

    inputPayload = { 'input': event }

    response = client.start_execution(
        stateMachineArn=stateMachineArn,
        input= json.dumps(inputPayload)
    )

    return {
        'statusCode': 200,
        'body': json.dumps('Kicked off Shipment Orchestration StepFunction from Lambda!')
    }
