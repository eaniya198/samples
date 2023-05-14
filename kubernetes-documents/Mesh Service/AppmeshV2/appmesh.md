<h1 align="center"> Appmesh </h1>
AWS App Mesh는 여러 유형의 컴퓨팅 인프라에서 서비스가 서로 쉽게 통신할 수 있도록 애플리케이션 레벨 네트워킹을 제공하는 서비스 메시입니다. 또한 애플리케이션에 대한 전체적인 가시성과 고가용성을 제공합니다. 또한 오픈 소스 프록시인 Envoy를 사용하여 마이크로 서비스 연결 및 모니터링을 위한 다양한 AWS 파트너 및 오픈 소스 도구와 호환됩니다.

## Components of App Mesh
- Service mesh
- Virtual services
- Virtual nodes
- Envoy Proxy
- Virtual Routers
- Routes

## 실습 시작
1. AWS 계정 연결
```
aws configure
```
2. EKS 클러스터 생성
```
eksctl create cluster --name mesh-test-cluster --version 1.24 --region ap-northeast-2 --zones ap-northeast-2a,ap-northeast-2b --nodegroup-name cls-nodes --node-type t3.small --nodes 2
```
<p align="center"><img src="https://github.com/jeonilshin/Kubernetes/assets/86287920/ea8302dc-1e9b-4ba8-8f7d-172dc079289c"></p>

클러스터 연결하기
```
aws eks --region ap-northeast-2 update-kubeconfig --name mesh-test-cluster
```
<p align="center"><img src="https://github.com/jeonilshin/Kubernetes/assets/86287920/de1e5b07-a90b-4602-8af7-d57cd6d827e7"></p>

3. Helm으로 eks-charts 리포지토리 추가하기
```
kubectl apply -k "https://github.com/aws/eks-charts/stable/appmesh-controller/crds?ref=master"
```
4. appmesh-system이란 Namespace 생성하기
```
kubectl create ns appmesh-system
```
5. OIDC 생성하기
```
eksctl utils associate-iam-oidc-provider --region=ap-northeast-2 --cluster mesh-test-cluster --approve
```
6. [AWSAppMeshFullAccess]과 [AWSCloudMapFullAccess] IAM 권한으로 IAM 역할을 만들고, appmesh-controller이란 Kubernetes Service Account으로 연결합니다.
```
eksctl create iamserviceaccount \
    --cluster mesh-test-cluster \
    --namespace appmesh-system \
    --name appmesh-controller \
    --attach-policy-arn  arn:aws:iam::aws:policy/AWSCloudMapFullAccess,arn:aws:iam::aws:policy/AWSAppMeshFullAccess \
    --override-existing-serviceaccounts \
    --approve
```
[AWSAppMeshFullAccess]: https://console.aws.amazon.com/iam/home?#policies/arn:aws:iam::aws:policy/AWSAppMeshFullAccess%24jsonEditor
[AWSCloudMapFullAccess]: https://console.aws.amazon.com/iam/home?#policies/arn:aws:iam::aws:policy/AWSCloudMapFullAccess%24jsonEditor

7. appmesh-controller 배포하기
```
helm upgrade -i appmesh-controller eks/appmesh-controller \
    --namespace appmesh-system \
    --set region=ap-south-1 \
    --set serviceAccount.create=false \
    --set serviceAccount.name=appmesh-controller
```
Appmesh Controller가 running으로 되어 있는지 확인합니다.
```
kubectl get deploy,pods -n appmesh-system
```
<p align="center"><img src="https://github.com/jeonilshin/Kubernetes/assets/86287920/8411eb99-7eaf-48d3-93ba-c4daf2db50e5"></p>

8. Mesh 생성하기
```
apiVersion: appmesh.k8s.aws/v1beta2
kind: Mesh
metadata:
  name: knol-mesh
spec:
  namespaceSelector:
    matchLabels:
      mesh: knol-mesh 
```
Mesh 확인하기
```
aws appmesh list-meshes
```
<p align="center"><img src="https://github.com/jeonilshin/Kubernetes/assets/86287920/93232c29-24ab-4524-8fe3-3c5b89d400b5"></p>

9. Namespace에 아래와 같은 Label을 추가하여 Sidecar Injection을 활성화/비활성화할 수 있습니다.
```
apiVersion: v1
kind: Namespace
metadata:
  name: mesh-workload
  labels:
    appmesh.k8s.aws/sidecarInjectorWebhook: enabled
```
<p align="center"><img src="https://github.com/jeonilshin/Kubernetes/assets/86287920/12947094-fd12-488b-aa5f-da2a072153b0"></p>

**Note:** Injection을 활성화한 후에는 메쉬 구성요소를 제자리에 배치해야 합니다. 그렇지 않으면 기존 포드가 종료되면 메쉬 리소스를 기다리는 동안 나타나지 않습니다.
<p align="center"><img src="https://github.com/jeonilshin/Kubernetes/assets/86287920/d493ee7c-e55d-4a0e-a147-2fd4b30b69b4" width="800"></p>

10. Virtual Node
```
apiVersion: appmesh.k8s.aws/v1beta2
kind: VirtualNode
metadata:
  name: knol-service
  namespace: mesh-workload
spec:
  awsName: knol-service-virtual-node
  podSelector:
    matchLabels:
      app: knol-service
  listeners:
    - portMapping:
        port: 80
        protocol: http
  serviceDiscovery:
    dns:
      hostname: knol-service.mesh-workload.svc.cluster.local
```
11. Virtual Router and Route
```
apiVersion: appmesh.k8s.aws/v1beta2
kind: VirtualRouter
metadata:
  namespace: mesh-workload
  name: knol-service
spec:
  awsName: knol-service-virtual-router
  listeners:
    - portMapping:
        port: 80
        protocol: http
  routes:
    - name: route
      httpRoute:
        match:
          prefix: /
        action:
          weightedTargets:
            - virtualNodeRef:
                name: knol-service
              weight: 1
```
12. Virtual Service
```
apiVersion: appmesh.k8s.aws/v1beta2
kind: VirtualService
metadata:
  name: knol-service
  namespace: mesh-workload
spec:
  awsName: knol-service-virtual-service
  provider:
    virtualRouter:
      virtualRouterRef:
        name: knol-service
```
13. Service Account 생성하기
```
apiVersion: v1
kind: ServiceAccount
metadata:
  name: knol-service
  namespace: mesh-workload
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::Account_ID:role/appmesh_role
```
14. 워크로드 배포하기
```
apiVersion: v1
kind: Service
metadata:
  name: knol-service
  namespace: mesh-workload
  labels:
    app: knol-service
spec:
  selector:
    app: knol-service
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: knol-service
  namespace: mesh-workload
  labels:
    app: knol-service
spec:
  replicas: 1
  selector:
    matchLabels:
      app: knol-service
  template:
    metadata:
      labels:
        app: knol-service
    spec:
      serviceAccountName: knol-service
      containers:
      - name: nginx
        image: nginx:1.19.0
        ports:
          - containerPort: 80
```
<p align="center"><img src="https://github.com/jeonilshin/Kubernetes/assets/86287920/71941300-a10a-4609-b10b-a3ec197ec771"></p>

결론, 클러스터의 모든 서비스가 해당 서비스 이름을 호출하여 서로 통신할 수 있습니다.
```
curl --head http://knol-service
```
<p align="center"><img src="https://github.com/jeonilshin/Kubernetes/assets/86287920/137dd0ad-7196-499b-8084-90aae4077786"></p>