## HorizontalPodAutoscaler
- refor
  
  https://kubernetes.io/ko/docs/tasks/run-application/horizontal-pod-autoscale/

  https://github.com/kubernetes-sigs/metrics-server



1. install metric server

    ```sh
    wget https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
    sed -i -e '136i\--kubelet-insecure-tls' components.yaml
    kubectl apply -f ./components.yaml
    ```

2. Create hpa.yml (yml) 
    ```yaml
    apiVersion: autoscaling/v1
    kind: HorizontalPodAutoscaler
    metadata:
      name: APP-hpa
      namespace: NAMESPACE
    spec:
      scaleTargetRef:
        apiVersion: apps/v1
        kind: Deployment
        name: APP-deployment
      minReplicas: 3
      maxReplicas: 5
      targetCPUUtilizationPercentage: 70
      ```

3. Create hpa (cli)
    ```bash
    kubectl autoscale rs foo --min=2 --max=5 --cpu-percent=80
    ```


4. Apply Deployment
    ```sh
    kubectl apply -f ./hpa.yml
    ```

------------

### resource metric
```yaml
type: ContainerResource
containerResource:
name: cpu
container: application
target:
    type: Utilization
    averageUtilization: 60
```


### scaling policy
PeriodSeconds represents the period during which the policy must remain true. The first policy allows (pads) to scale down up to four replica's in a minute. The second policy allows up to 10% of the current replica to be scaled down in one minute at a rate.
```yaml
behavior:
  scaleDown:
    policies:
    - type: Pods
      value: 4
      periodSeconds: 60
    - type: Percent
      value: 10
      periodSeconds: 60
```

### Stabilization window
The stabilization window is used to limit the shaking of the replica number when the metric used for scaling continues to fluctuate.
```yml
behavior:
  scaleDown:
    stabilizationWindowSeconds: 300
```


