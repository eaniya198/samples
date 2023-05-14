## codedeploy agent install

```bash
#!/bin/bash

yum update -y
yum install ruby wget -y

cd /home/ec2-user
wget https://aws-codedeploy-us-east-1.s3.us-east-1.amazonaws.com/latest/install
chmod +x ./install
./install auto

systemctl enable codedeploy-agent --now
```

## install pypy3

```bash
#!/bin/bash
cd /etc

wget https://downloads.python.org/pypy/pypy3.9-v7.3.11-linux64.tar.bz2
tar -xf pypy3.9-v7.3.11-linux64.tar.bz2
ln -s /etc/pypy3.9-v7.3.11-linux64/bin/pypy3.9 /usr/bin/pypy3
pypy3 -m ensurepip

```

## Application spec

port: 5000
healthcheck api: /healthcheck (should not be public)

## Deploy steps

1. VPC
2. ALB & target group
3. ASG
4. CodePipeline
