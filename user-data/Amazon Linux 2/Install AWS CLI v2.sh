#!/bin/bash

curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

sudo rm -rf /usr/bin/aws*
sudo ln -s /usr/local/bin/aws /usr/bin/
sudo ln -s /usr/local/bin/aws_completer /usr/bin/