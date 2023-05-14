## Secondary IP Control

- refor

    https://docs.aws.amazon.com/ko_kr/eks/latest/userguide/managing-vpc-cni.html

    https://github.com/aws/amazon-vpc-cni-k8s/blob/master/docs/eni-and-ip-target.md

1. pod limit
    ```bash
    #!/bin/bash
    /etc/eks/bootstrap.sh YourEKSName --use-max-pods false --kubelet-extra-args '--max-pods=10'
    ```

2. Secondary IP limit

    WARM_IP_TARGET: Assign 2 additional secondary IPs each time Pod is created
MINIMUM_IP_TARGET: Sets the number of pods normally maintained in the Node instance. Assign secondary IPs to ENIs in advance of that number
    ```bash
    kubectl set env ds aws-node -n kube-system WARM_IP_TARGET=2 
    kubectl set env ds aws-node -n kube-system MINIMUM_IP_TARGET=10
    ```