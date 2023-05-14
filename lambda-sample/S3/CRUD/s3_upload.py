import boto3

s3_client = boto3.client('s3')

# 업로드 할 파일
file_name = "./dist2.png"

# S3에 업로드시 바뀔 이름
change_file_name = "worldskills.png"

# S3 Bucket이름
bucket_Name = "test.s3.buckets.123"

# S3에 업로드하기
s3_client.upload_file(file_name, bucket_Name, change_file_name)