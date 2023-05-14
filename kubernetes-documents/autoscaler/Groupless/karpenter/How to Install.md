# 환경변수 지정

// https://karpenter.sh/ 해당 사이트에서 버전 확인 후 진행
```
export KARPENTER_VERSION=v0.26.1
export CLUSTER_NAME="lion-cluster"
export CLUSTER_ENDPOINT="$(aws eks describe-cluster --name ${CLUSTER_NAME} --query "cluster.endpoint" --output text)"
export AWS_DEFAULT_REGION="ap-northeast-2"
export AWS_ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
```

# 노드가 생성될 서브넷, 사용할 보안 그룹에 태깅 작업
karpenter.sh/discovery = ${CLUSTER_NAME}

# Karpenter가 생성할 노드에 붙일 IAM Role 생성
TEMPOUT=$(mktemp)

curl -fsSL https://karpenter.sh/"${KARPENTER_VERSION}"/getting-started/getting-started-with-eksctl/cloudformation.yaml  > $TEMPOUT \
&& aws cloudformation deploy \
  --stack-name "Karpenter-${CLUSTER_NAME}" \
  --template-file "${TEMPOUT}" \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides "ClusterName=${CLUSTER_NAME}"

eksctl create iamidentitymapping \
  --username system:node:{{EC2PrivateDNSName}} \
  --cluster "${CLUSTER_NAME}" \
  --arn "arn:aws:iam::${AWS_ACCOUNT_ID}:role/KarpenterNodeRole-${CLUSTER_NAME}" \
  --group system:bootstrappers \
  --group system:nodes

 eksctl create iamserviceaccount \
  --cluster "${CLUSTER_NAME}" --name karpenter --namespace karpenter \
  --role-name "${CLUSTER_NAME}-karpenter" \
  --attach-policy-arn "arn:aws:iam::${AWS_ACCOUNT_ID}:policy/KarpenterControllerPolicy-${CLUSTER_NAME}" \
  --role-only \
  --approve


# Spot Service LIned Role 생성 (EC2 Spot 처음 쓰는 계정에서 필요함)
aws iam create-service-linked-role --aws-service-name spot.amazonaws.com || true

# Karpenter 설치
helm install karpenter oci://public.ecr.aws/karpenter/karpenter --version v0.27.3 --namespace karpenter --create-namespace \
  --debug log \
  --set serviceAccount.annotations."eks\.amazonaws\.com/role-arn"="arn:aws:iam::216713689620:role/lion-cluster-karpenter" \
  --set clusterName=${CLUSTER_NAME} \
  --set clusterEndpoint=${CLUSTER_ENDPOINT} \
  --set aws.defaultInstanceProfile=KarpenterNodeInstanceProfile-${CLUSTER_NAME} \
  --wait

