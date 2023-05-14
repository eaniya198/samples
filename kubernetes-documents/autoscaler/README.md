# Cluster HPA

## Install Metrics server & Cluster autoscaler

```bash
#!/bin/bash -eux

# Install metrics server
helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/
helm upgrade --install metrics-server metrics-server/metrics-server -n kube-system $HELM_TOLERATION

# Craete IAM poilcy for IRSA
cat << EOF > /tmp/cluster-autoscaler-policy.json
{
    "Version": "2012-10-17",
    "Statement": [
        {
        "Effect": "Allow",
        "Action": [
            "autoscaling:DescribeAutoScalingGroups",
            "autoscaling:DescribeAutoScalingInstances",
            "autoscaling:DescribeLaunchConfigurations",
            "autoscaling:DescribeTags",
            "ec2:DescribeInstanceTypes",
            "ec2:DescribeLaunchTemplateVersions"
        ],
        "Resource": ["*"]
        },
        {
        "Effect": "Allow",
        "Action": [
            "autoscaling:SetDesiredCapacity",
            "autoscaling:TerminateInstanceInAutoScalingGroup",
            "ec2:DescribeImages",
            "ec2:GetInstanceTypesFromInstanceRequirements",
            "eks:DescribeNodegroup"
        ],
        "Resource": ["*"]
        }
    ]
}
EOF

aws iam create-policy \
--policy-name AmazonEKSClusterAutoscalerPolicy \
--policy-document file:///tmp/cluster-autoscaler-policy.json

# Create IRSA
eksctl create iamserviceaccount \
    --cluster=$CLUSTER \
    --namespace=kube-system \
    --name=cluster-autoscaler \
    --attach-policy-arn=arn:aws:iam::$AWS_ACCOUNT_ID:policy/AmazonEKSClusterAutoscalerPolicy \
    --override-existing-serviceaccounts \
    --approve

# Install Cluster Autoscaler
helm repo add autoscaler https://kubernetes.github.io/autoscaler

KUBE_VERSION=$(kubectl version -o json | jq -rj '.serverVersion|.gitVersion[:5],".0"')

helm upgrade --install aws-cluster-autoscaler autoscaler/cluster-autoscaler -n kube-system \
--set autoDiscovery.clusterName=$CLUSTER \
--set awsRegion=$(aws configure get region) \
--set rbac.serviceAccount.create=false \
--set rbac.serviceAccount.name=cluster-autoscaler \
--set extraArgs.ignore-daemonsets-utilization=true \
--set image.tag=$KUBE_VERSION \
$HELM_TOLERATION
```
