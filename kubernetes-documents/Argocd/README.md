# ARGO CD

## Installation

```bash
#!/bin/bash -eux

# Install Argo CD
kubectl create namespace argocd
helm repo add argo https://argoproj.github.io/argo-helm

helm upgrade --install argocd -n argocd argo/argo-cd \
--set crds.keep=false \
--set global.tolerations\[0\].key="$TOLERATION_KEY" \
--set global.tolerations\[0\].value="$TOLERATION_VALUE" \
--set global.tolerations\[0\].effect="NoSchedule" \
--set global.nodeSelector.$TOLERATION_KEY=$TOLERATION_VALUE

# Install Argo CD CLI
VERSION=$(curl --silent "https://api.github.com/repos/argoproj/argo-cd/releases/latest" | grep '"tag_name"' | sed -E 's/.*"([^"]+)".*/\1/')
sudo curl --silent --location -o /usr/local/bin/argocd https://github.com/argoproj/argo-cd/releases/download/$VERSION/argocd-linux-$ARCH
sudo chmod +x /usr/local/bin/argocd

# Add ssh certs for argocd to use CodeCommit as a repository
ssh-keyscan "git-codecommit.$(aws configure get region).amazonaws.com" | argocd cert add-ssh --batch
```

## argocd-server access

Expose argocd-server service using Classic Load Balancer

```bash
kubectl patch svc argocd-server -n argocd -p '{"spec": {"type": "LoadBalancer"}}'
```

Port forward requests to argocd-server service. You can allow external requests using `--address` option

```bash
kubectl port-forward service/argocd-server -n argocd 8080:443
```

## argocd cli login to server

```bash
## exposing server endpoint
# export ARGOCD_SERVER=$(kubectl get svc argocd-server -n argocd -o json | jq --raw-output .status.loadBalancer.ingress[0].hostname)

# not exposing, but port-forwarding
export ARGOCD_SERVER="localhost:8080"
export ARGO_PWD=$(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d)

argocd login $ARGOCD_SERVER --username admin --password $ARGO_PWD --insecure
```

## Argocd repository & application

- Consideration
  - Allow **outbound ssh** of argocd node. If a vpc endpoint is configured, allow **inbound ssh** of endpoint ENI.
  - SSH_GIT_REPOSITORY looks like `ssh://<USER>@<GIT_REPOSITORY>`.
  - Configuring your argocd appilcation with **kustomize** is recommended.
  - If you want to apply all files of subdirectory, use `--directory-recurse` option.


```bash
#!/bin/bash -eux
SSH_GIT_REPOSITORY=''
SSH_KEY_PATH='~/.ssh/id_rsa'
APPLICATION_NAME=''
MANIFEST_PATH='./'
NAMESPACE=''

argocd repo add $SSH_GIT_REPOSITORY --name $APPLICATION_NAME --ssh-private-key-path $SSH_KEY_PATH

argocd app create $APPLICATION_NAME --repo $SSH_GIT_REPOSITORY --path $MANIFEST_PATH --dest-server https://kubernetes.default.svc --dest-namespace $NAMESPACE --sync-policy automated --self-heal --auto-prune
```