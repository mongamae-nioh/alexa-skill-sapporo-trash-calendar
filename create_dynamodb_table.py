import boto3

dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')

try:
    table = dynamodb.create_table(
        TableName='SapporoTrashCalendar',
        KeySchema=[
            {
                'AttributeName': 'WardCalNo',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'Date',
                'KeyType': 'RANGE'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'WardCalNo',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'Date',
                'AttributeType': 'S'
            },
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1
        }
    )

    print("Table status:", table.table_status)

except Exception as e:
    print("Error creating table:", e)