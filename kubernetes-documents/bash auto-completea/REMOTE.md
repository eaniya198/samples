## kubernetes 자동완성 패키지
- refor

    https://github.com/Piotr1215/kubectl-container

    bash-completion 
    ```sh
    source /usr/share/bash-completion/bash_completion
    ```

1. Enable AutoComplete

    1-1. Current User
    ```sh
    echo 'source <(kubectl completion bash)' >>~/.bashrc
    ```
    1-12. System-wide
    ```sh
    kubectl completion bash | sudo tee /etc/bash_completion.d/kubectl > /dev/null
    ```
2. Enable bash auto-complete
    ```
    exec bash
    ```
3. Test Behavior
    ```
    k
    ```

    output
    ```sh
    kubectl controls the Kubernetes cluster manager.

    Find more information at: https://kubernetes.io/docs/reference/kubectl/

    Basic Commands (Beginner):
    create          Create a resource from a file or from stdin
    expose          Take a replication controller, service, deployment or pod and expose it as a new
    Kubernetes service
    run             Run a particular image on the cluster
    set             Set specific features on objects

    Basic Commands (Intermediate):
    explain         Get documentation for a resource
    get             Display one or many resources
    edit            Edit a resource on the server
    delete          Delete resources by file names, stdin, resources and names, or by resources and
    label selector
    ~~~~
    ```