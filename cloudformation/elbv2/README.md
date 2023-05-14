# ALB Access Log

To enable access log, you must allow AWS Logging Account to access the bucket.

Apply the following policy to the target bucket.
According to the region, ELB_ACCOUNT_ID varies. Check this [page](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/enable-access-logging.html#attach-bucket-policy)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::ELB_ACCOUNT_ID:root"
      },
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::BUCKET_NAME/AWSLogs/ACCOUNT_ID/*"
    }
  ]
}
```
