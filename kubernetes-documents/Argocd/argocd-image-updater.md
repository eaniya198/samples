# ArgoCD Image Updater

## Prerequisite

Manifests of ArgoCD application must be rendered using `Helm` or `Kustomize`

## Install

```bash
#!/bin/bash -eux
REGION=$(aws configure get region)

eksctl create iamserviceaccount \
--cluster=$CLUSTER \
--namespace=argocd \
--name=argocd-image-updater \
--attach-policy-arn=arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly \
--override-existing-serviceaccounts \
--approve

cat << EOF > /tmp/argocd-image-updater-values.yaml
config:
  argocd:
    serverAddress: "argocd-server"
  registries:
    - name: ECR
      api_url: https://$AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com
      prefix: $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com
      ping: yes
      insecure: no
      credentials: ext:/scripts/ecr.sh
      credsexpire: 10h
authScripts:
  enabled: true
  scripts:
    ecr.sh: |
      #!/bin/sh
      aws ecr --region $REGION get-authorization-token --output text --query 'authorizationData[].authorizationToken' | base64 -d
serviceAccount:
  create: false
  name: "argocd-image-updater"
nodeSelector:
  $TOLERATION_KEY: $TOLERATION_VALUE
tolerations:
  - key: $TOLERATION_KEY
    value: $TOLERATION_VALUE
    effect: NoSchedule
EOF

helm upgrade --install argocd-image-updater -n argocd argo/argocd-image-updater -f /tmp/argocd-image-updater-values.yaml

# Create account for image updater
cat << EOF > /tmp/argocd-cm.yaml
data:
  accounts.image-updater: apiKey
EOF

kubectl patch configmaps argocd-cm -n argocd --type merge --patch-file /tmp/argocd-cm.yaml

# Grant policy to account
cat << EOF > /tmp/argocd-rbac-cm.yaml
data:
  policy.csv: |
    p, role:image-updater, applications, get, */*, allow
    p, role:image-updater, applications, update, */*, allow
    g, image-updater, role:image-updater
  policy.default: role.readonly
EOF

kubectl patch configmap argocd-rbac-cm -n argocd --type merge --patch-file /tmp/argocd-rbac-cm.yaml

# Create secret for image updater
IMAGE_UPDATER_TOKEN=$(argocd account generate-token --account image-updater --id image-updater)

kubectl create secret generic argocd-image-updater-secret -n argocd --from-literal argocd.token=$IMAGE_UPDATER_TOKEN
```

### annotation

[ref](https://argocd-image-updater.readthedocs.io/en/stable/configuration/images/)

```bash
kubectl annotate applications <APP_NAME> -n argocd \
argocd-image-updater.argoproj.io/update-strategy=semver \
argocd-image-updater.argoproj.io/image-list=app=<IMAGE_URL>
```
