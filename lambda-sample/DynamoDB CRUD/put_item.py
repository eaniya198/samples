import boto3
import json

db = boto3.resource('dynamodb')
table = db.Table("test")

response = table.put_item(
    Item={
        'number': '3',
        'school': 'Gongju',
        'name': "sga"
    }
)

print(json.dumps(response, indent=4))