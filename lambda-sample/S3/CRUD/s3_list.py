import boto3

# S3 resource 생성
s3 = boto3.resource('s3')

for bucket in s3.buckets.all():
    print(bucket.name)