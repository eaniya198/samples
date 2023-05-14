## Taint kind
- **NoSchedule**

  -> The existing Pod is limited to the Pod, restricting schedule only to run forward.

- **NoExecute**
 
  -> Limits the scheduling of pods that will be created in the future, and releases all pods that were previously placed in that node

- **PreferNoSchedult**

   -> I allow existing running pods, and I don't prefer to schedule future pods, but I allow them if there's no other place to schedule except that node.


---
### Taint CLI

1. Add Taint
    ```sh
    kubectl taint node NodeName [key]=[value]:[effect]
    ```

2. Delete Taint
    ```sh
    kubectl taint node NodeName [key]=[value]:[effect]-
    ```

------

### Tollation

1. All kinds of tints are allowed.

    ```yml
    tolerations:
    - operator: Exists
    ```

2. Allow all Taint with Key as Role.
    ```yml
    tolerations:
    - key: role
        operator: Exists
    ```

3. Allow all Taint where Key is Role and Effect is NoExecute.
    ```yml
    tolerations:
    - ket: role
        operator: Exists
        effect: NoExecute
    ```

4. role=system:Allow NoscheduleTaint.
    ```yml
    tolerations:
    - key: role
      operator: Equal
      value: system
      effect: NoSchedule
    ```

-------

### example deployment
```yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tolerated
spec:
  replicas: 3
  selector:
    matchLabels:
      app: hello
  template:
    metadata:
      name: hello
      labels:
        app: hello
    spec:
      containers:
      - name: nginx
        image: nginxdemos/hello:plain-text
        ports:
        - name: http
          containerPort: 80
          protocol: TCP
      tolerations:
      - key: role
        operator: Equal
        value: system
        effect: NoSchedule
```