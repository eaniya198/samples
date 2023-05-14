import boto3
import json

def create_skills_table(dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000", region_name='ap-northeast-1')

    table = dynamodb.create_table(
        TableName='worldskills',
        KeySchema=[
            {
                'AttributeName': 'country',
                'KeyType': 'HASH'  # Partition key
            },
            {
                'AttributeName': 'code',
                'KeyType': 'RANGE'  # Sort key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'country',
                'AttributeType': 'kor'
            },
            {
                'AttributeName': 'code',
                'AttributeType': '1235'
            },

        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )
    return table


if __name__ == '__main__':
    skills_table = create_skills_table()
    print("Table status:", skills_table.table_status)