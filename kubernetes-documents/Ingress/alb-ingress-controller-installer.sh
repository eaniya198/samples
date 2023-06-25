#!/bin/bash
helm repo add eks https://aws.github.io/eks-charts
kubectl apply -k "github.com/aws/eks-charts/stable/aws-load-balancer-controller//crds?ref=master"
helm install aws-load-balancer-controller eks/aws-load-balancer-controller -n kube-system --set clusterName=day1-cluster \
--set serviceAccount.create=false \
--set serviceAccount.name=aws-load-balancer-controller \
--set region=ap-northeast-2 \
--set vpcId=vpc-0b3422f6660e7d316



# policy
# curl -O https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.4.7/docs/install/iam_policy.json
# aws iam create-policy \
# --policy-name AWSLoadBalancerControllerIAMPolicy \
# --policy-document file://iam_policy.json
# eksctl create iamserviceaccount \
#   --cluster=day1-cluster \
#   --namespace=kube-system \
#   --name=aws-load-balancer-controller \
#   --role-name AmazonEKSLoadBalancerControllerRole \
#   --attach-policy-arn=arn:aws:iam::216713689620:policy/AWSLoadBalancerControllerIAMPolicy \
#   --approve