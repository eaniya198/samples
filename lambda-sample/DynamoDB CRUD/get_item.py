import boto3
import json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table("boto3table")

response = table.get_item(
    Key={
        'school': 'Gongju',
        'number': '2'
    }
)
print(json.dumps(response["Item"], indent=4))