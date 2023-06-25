#!/bin/bash
CLUSTER_NAME="day1-cluster"
EKS_VERSION=$(aws eks describe-cluster --name $CLUSTER_NAME --query "cluster.version" --output text)

### SET UP TO METRIC SERVERS
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
kubectl patch deployment metrics-server -n kube-system --type=json -p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}]'

