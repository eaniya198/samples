#!/bin/bash

VPC_ID="vpc-0b3422f6660e7d316"
PUB_TAG_KEY="kubernetes.io/role/elb"
PUB_TAG_VALUE="1"
PRIV_TAG_KEY="kubernetes.io/role/internal-elb"
PRIV_TAG_VALUE="1"


subnet_ids=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query 'Subnets[].SubnetId' --output text)

for subnet_id in $subnet_ids; do
  subnet_names=$(aws ec2 describe-tags --filters "Name=resource-id,Values=$subnet_id" "Name=key,Values=Name" --query 'Tags[].Value' --output text)
  subnet_name=$(aws ec2 describe-tags --filters "Name=resource-id,Values=$subnet_id" "Name=key,Values=Name" --query 'Tags[].Value' --output text | tr '[A-Z]' '[a-z]')
  if [[ $subnet_name == *private* ]] || [[ $subnet_name == *pri* ]]; then
    aws ec2 create-tags --resources $subnet_id --tags Key=$PRIV_TAG_KEY,Value=$PRIV_TAG_VALUE
    echo "Added tag to Private subnet: $subnet_id"

  elif [[ $subnet_name == *public*]] || [[$subnet_name == *pub* ]]; then
    aws ec2 create-tags --resources $subnet_id --tags Key=$PUB_TAG_KEY,Value=$PUB_TAG_VALUE
    echo "Added tag to Public subnet: $subnet_id"    
  fi
done
