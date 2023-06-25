kubectl apply -f https://raw.githubusercontent.com/aws-samples/amazon-cloudwatch-container-insights/master/k8s-yaml-templates/cloudwatch-namespace.yaml

eksctl create iamserviceaccount \
--name cwagent-prometheus \
--namespace amazon-cloudwatch \
 --cluster day1-cluster \
 --attach-policy-arn arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy \
 --approve \
 --override-existing-serviceaccounts

kubectl create configmap cluster-info \
--from-literal=cluster.name=day1-cluster \
--from-literal=logs.region=ap-northeast-2 \
-n amazon-cloudwatch

kubectl apply -f https://raw.githubusercontent.com/aws-samples/amazon-cloudwatch-container-insights/master/k8s-yaml-templates/fluentd/fluentd.yaml
