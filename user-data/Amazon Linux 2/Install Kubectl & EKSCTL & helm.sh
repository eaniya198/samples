#!/bin/bash
curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/bin/

curl -O https://s3.us-west-2.amazonaws.com/amazon-eks/1.25.7/2023-03-17/bin/linux/amd64/kubectl
chmod +x ./kubectl
mv ./kubectl /usr/bin/

curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

###### Helm Downgrade #######
## initArch() {
##   ARCH=$(uname -m)
##   case $ARCH in
##     armv5*) ARCH="armv5";;
##     armv6*) ARCH="armv6";;
##     armv7*) ARCH="arm";;
##     aarch64) ARCH="arm64";;
##     x86) ARCH="386";;
##     x86_64) ARCH="amd64";;
##     i686) ARCH="386";;
##     i386) ARCH="386";;
##   esac
## } 
## initArch
## curl -o helm-3.8.2.tar.gz https://get.helm.sh/helm-v3.8.2-linux-${ARCH}.tar.gz 
## tar -zxf helm-3.8.2.tar.gz 
## chmod 777 ./linux-amd64/helm
## mv ./linux-amd64/helm /usr/bin/
## helm version