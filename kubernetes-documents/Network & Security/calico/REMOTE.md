## Using Calico CNI after VPN CNI Delete

### **preconditions**
The operation should be carried out without Node.

1. Delete the existing VPC CNI installed.
   ```sh
   kubectl delete daemonset -n kube-system aws-node
   ```

2. Install the Calico CNI.
   ```sh
   kubectl apply -f https://raw.githubusercontent.com/projectcalico/calico/v3.25.1/manifests/calico-vxlan.yaml
   ```
   
3. Now set up node groups
   ```sh
   eksctl create nodegroup --cluster my-calico-cluster --node-type t3.medium --max-pods-per-node 100
   ```

----

**Calico Network Policy:** Namespace resources that apply to pods/containers/VMs in that namespace.

   ```yaml
  apiVersion: projectcalico.org/v3
  kind: NetworkPolicy
  metadata:
    name: allow-tcp-6379
    namespace: production
   ```


**Calico Global Network Policy:** Resources without namespace

   ```yaml
  apiVersion: projectcalico.org/v3
  kind: GlobalNetworkPolicy
  metadata:
    name: allow-tcp-port-6379
   ```

-------

## calico install

- refor

   https://docs.aws.amazon.com/eks/latest/userguide/calico.html

   https://docs.tigera.io/calico/latest/getting-started/kubernetes/helm#install-calico

1. install calico & calicoctl
   ```sh
   helm repo add projectcalico https://docs.tigera.io/calico/charts
   kubectl create namespace tigera-operator
   helm install calico projectcalico/tigera-operator --version v3.25.1 --namespace tigera-operator
   curl -L https://github.com/projectcalico/calico/releases/latest/download/calicoctl-linux-amd64 -o calicoctl
   chmod +x ./calicoctl
   ```

2. calicoctl test
   ```sh
   ./calicoctl version
   ```
   output
   ```
   Client Version:    v3.25.1
   Git commit:        82dadbce1
   Cluster Version:   v3.25.1
   Cluster Type:      k8s,kdd,typha,operator
   ```

------

