import boto3
import json

lambda_client = boto3.client('lambda', region_name='ap-northeast-1')

response = lambda_client.invoke(
            FunctionName='Test1',
            InvocationType='Event',
            Payload=json.dumps(
                {
                    "key1": "value1",
                    "key2": "value2",
                    "key3": "value3"
                }
            )
)  

print(response)