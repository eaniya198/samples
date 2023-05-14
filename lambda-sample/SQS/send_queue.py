import boto3
sqs = boto3.client('sqs')
queue_url = 'https://sqs.us-west-2.amazonaws.com/635272395604/skills-queue'

resp = sqs.send_message(
    QueueUrl=queue_url,
    MessageBody=(
        'Sample message for Queue.'
    )
)

print(resp['MessageId'])