
# Cluodwatch Agent daemonset

## Install CWAgent 
```bash
#!/bin/bash -eux
# Create namespace for CWAgent
kubectl create namespace amazon-cloudwatch || true

# Create IRSA for CWAgent
kubectl apply -f https://raw.githubusercontent.com/aws-samples/amazon-cloudwatch-container-insights/latest/k8s-deployment-manifest-templates/deployment-mode/daemonset/container-insights-monitoring/cwagent/cwagent-serviceaccount.yaml

eksctl create iamserviceaccount \
  --cluster=$CLUSTER \
  --namespace=amazon-cloudwatch \
  --name=cloudwatch-agent \
  --attach-policy-arn=arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy \
  --override-existing-serviceaccounts \
  --approve

# Download CWAgent configmap
curl -so /tmp/cwagent-configmap.yaml https://raw.githubusercontent.com/aws-samples/amazon-cloudwatch-container-insights/latest/k8s-deployment-manifest-templates/deployment-mode/daemonset/container-insights-monitoring/cwagent/cwagent-configmap.yaml

sed -i 's/{{cluster_name}}/'$CLUSTER'/' /tmp/cwagent-configmap.yaml

kubectl apply -f /tmp/cwagent-configmap.yaml

# Download CWAgent daemonset and deploy to cluster
curl -so /tmp/cwagent-daemonset.yaml https://raw.githubusercontent.com/aws-samples/amazon-cloudwatch-container-insights/latest/k8s-deployment-manifest-templates/deployment-mode/daemonset/container-insights-monitoring/cwagent/cwagent-daemonset.yaml

cat << EOF >> /tmp/cwagent-daemonset.yaml
      tolerations:
        - key: node-role.kubernetes.io/master
          operator: Exists
          effect: NoSchedule
        - operator: "Exists"
          effect: "NoExecute"
        - operator: "Exists"
          effect: "NoSchedule"
EOF

kubectl apply -f /tmp/cwagent-daemonset.yaml
```
