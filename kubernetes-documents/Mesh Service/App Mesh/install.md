1. Helm에 eks-chart 추가
```
$ helm repo add eks https://aws.github.io/eks-charts
```

2. App Mesh Controller를 설치하기
```
$ kubectl create ns appmesh-system
$ helm upgrade -i appmesh-controller eks/appmesh-controller -n appmesh-system \
--set serviceAccount.create=false \
--set serviceAccount.name=appmesh-controller \ 
--set regoin=ap-northeast-2
$ kubectl get pods -n appmesh-system
```

3. ns에 sidecar injection label 적용
app에 envoy sidecar를 적용하려면 해당 app이 설치된 namespace에 label을 적용시켜줘야 한다. 아래와 같이 애플리케이션에 적용될 mesh 이름과 사이트카 Injector webhook을 활성화하는 Label을 적용해주자.
```
$ kubectl label namespace yelb mesh=yelb
$ kubectl label namespace yelb appmesh.k8s.aws/sidecarInjectorWebhook=enabled
$ kubectl get namespaces --show-labels | grep yelb
```

4. App Mesh 컴포넌트 등록

Mesh 생성 -> VirtualNode -> VirtualService -> VIrtualRouter
- 가상 노드의 name은 가상 라우터의 routes.httpRoute.action.weightedTargets.virtualNodeRef.name과 동일해야 한다.
- 가상 노드의 serviceDiscovery.dns.hostname은 가상 서비스의 awsName과 동일해야 한다.
- 가상 라우터의 name은 가상 서비스의 provider.virtualRouter.virtualRouterRef.name과 동일해야 한다.



5. Envoy Sidecar 주입

우선 Proxt 인증 활성화 해준다.
```
$ ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
$ VIRTUAL_NODE_NAME="gm-skills-virtual-node"
$ APPMESH_NAME="gm-skills"
$ CLUSTER_NAME="gm-skills-cluster"
$ cat << EOF > proxy-auth.json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "appmesh:StreamAggregatedResources",
            "Resource": [
                "arn:aws:appmesh:ap-northeast-2:${ACCOUNT_ID}:mesh/${APPMESH_NAME}/virtualNode/${VIRTUAL_NODE_NAME}"
            ]
        }
    ]
}
EOF

$ aws iam create-policy --policy-name appmesh-proxy-auth --policy-document file://proxy-auth.json

$ eksctl create iamserviceaccount \
     --cluster $CLUSTER_NAME \
     --namespace gm-skills \
     --name gm-skills-mesh-role \
     --attach-policy-arn  arn:aws:iam::${ACCOUNT_ID}:policy/appmesh-proxy-auth \
     --override-existing-serviceaccounts \
     --approve \
     --region ap-northeast-2
```

아래와 같이 Service Account를 추가해준다.
```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gm-skills-deployment
  namespace: gm-skills
spec:
  replicas: 3
  selector:
    matchLabels:
      app.kubernetes.io/name: gm-skills
  template:
    metadata:
      labels:
        app.kubernetes.io/name: gm-skills
        app.kubernetes.io/version: "v1.0"
    spec:
      serviceAccountName: gm-skills-mesh-role
```

Pod를 새로 띄우면 자동으로 주입된다. READY가 1/1에서 2/2로 변경되는 것을 볼 수 있다.
```
$ kubectl rollout restart deployment -n yelb
```


6. Virtual Gateway & GatewayRouter




# Monitoring
```bash
$ AUTOSCALING_GROUP=$(aws eks describe-nodegroup --cluster-name demo-mesh-cluster --nodegroup-name demo-mesh-cluster-ng | jq -r '.nodegroup.resources.autoScalingGroups[0].name')
$ ROLE_NAME=$(aws iam get-instance-profile --instance-profile-name $AUTOSCALING_GROUP | jq -r '.InstanceProfile.Roles[] | .RoleName')
$ aws iam attach-role-policy \
      --role-name $ROLE_NAME \
      --policy arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess
```

### App Mesh data plane의 X-Ray Tracing 활성화

```bash
$ helm uninstall appmesh-controller -n appmesh-system
$ helm upgrade -i appmesh-controller eks/appmesh-controller \
    --namespace appmesh-system \
    --set tracing.enabled=true \
    --set tracing.provider=x-ray \
    --namespace appmesh-system \
    --set region=ap-northeast-1 \
    --set serviceAccount.create=false \
    --set serviceAccount.name=appmesh-controller
$ kubectl rollout restart deployment -n yelb
```
