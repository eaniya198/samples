IAM Policy 생성
아래와 같이 cluster-autoscaler-policy.json 파일을 생성한다.
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "autoscaling:DescribeAutoScalingGroups",
                "autoscaling:DescribeAutoScalingInstances",
                "autoscaling:DescribeLaunchConfigurations",
                "autoscaling:DescribeTags",
                "autoscaling:SetDesiredCapacity",
                "autoscaling:TerminateInstanceInAutoScalingGroup",
                "ec2:DescribeLaunchTemplateVersions"
            ],
            "Resource": "*",
            "Effect": "Allow"
        }
    ]
}
```

아래와 같이 policy 를 생성한다.
```
aws iam create-policy \
    --policy-name AmazonEKSClusterAutoscalerPolicy \
    --policy-document file://cluster-autoscaler-policy.json
```
위 command 를 실행하고 나오는 output 에서 Amazon Resource Name (ARN)을 아

```
eksctl create iamserviceaccount \
  --cluster=eks-demo \
  --namespace=kube-system \
  --name=cluster-autoscaler \
  --attach-policy-arn=<위에서 생성한 policy의 arn> \
  --override-existing-serviceaccounts \
  --approve

curl -o cluster-autoscaler-autodiscover.yaml https://raw.githubusercontent.com/kubernetes/autoscaler/master/cluster-autoscaler/cloudprovider/aws/examples/cluster-autoscaler-autodiscover.yaml

vim cluster-autoscaler-autodiscover.yaml
<YOUR CLUSTER NAME> 항목을 Cluster의 이름으로 변경
kubectl apply -f cluster-autoscaler-autodiscover.yaml

kubectl patch deployment cluster-autoscaler \
  -n kube-system \
  -p '{"spec":{"template":{"metadata":{"annotations":{"cluster-autoscaler.kubernetes.io/safe-to-evict": "false"}}}}}'

kubectl -n kube-system edit deployment.apps/cluster-autoscaler

아래와 같이 --balance-similar-node-groups, --skip-nodes-with-system-pods 옵션을 추가
    spec:
      containers:
      - command
        - ./cluster-autoscaler
        - --v=4
        - --stderrthreshold=info
        - --cloud-provider=aws
        - --skip-nodes-with-local-storage=false
        - --expander=least-waste
        - --node-group-auto-discovery=asg:tag=k8s.io/cluster-autoscaler/enabled,k8s.io/cluster-autoscaler/<YOUR CLUSTER NAME>
        - --balance-similar-node-groups
        - --skip-nodes-with-system-pods=false
```
그리고 아래 release링크를 참고해 cluster 버전을 지원하는 버전으로 변경
```
kubectl set image deployment cluster-autoscaler \
  -n kube-system \
  cluster-autoscaler=k8s.gcr.io/autoscaling/cluster-autoscaler:v1.25.1

kubectl -n kube-system logs -f deployment.apps/cluster-autoscaler
```
