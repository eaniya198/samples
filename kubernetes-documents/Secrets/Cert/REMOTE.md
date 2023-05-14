
## Create Secret


refer

- https://kubernetes.io/docs/tasks/configmap-secret/managing-secret-using-kubectl/

1. add username.txt, password.txt
    ```
    # The -n option prevents additional open characters from being included at the end of the text.
    echo -n 'admin' > ./username.txt
    echo -n '1f2d1e2e67df' > ./password.txt
    ```

2. Create secret
    ```
    kubectl create secret generic db-user-pass \
    --from-file=./username.txt \
    --from-file=./password.txt
    ```

    output
    ```
    secret/db-user-pass created
    ```

## Decode Secret

refer

- https://kubernetes.io/docs/tasks/configmap-secret/managing-secret-using-kubectl/


1. View the contents of the Secret you created
    ```
    kubectl get secret db-user-pass -o jsonpath='{.data}'
    ```

    output
    ```
    { "password": "UyFCXCpkJHpEc2I9", "username": "YWRtaW4=" }
    ```


2. Decode the password data
    ```
    echo 'UyFCXCpkJHpEc2I9' | base64 --decode
    ```

    output
    ```
    S!B\*d$zDsb=
    ```

## Edit a Secret


refer

- https://kubernetes.io/docs/tasks/configmap-secret/managing-secret-using-kubectl/

1. Edit Default Object Secret
    ```
    kubectl edit secrets <secret-name>
    ```
    output
    ```
    # Please edit the object below. Lines beginning with a '#' will be ignored,
    # and an empty file will abort the edit. If an error occurs while saving this file, it will be
    # reopened with the relevant failures.
    #
    apiVersion: v1
    data:
    password: UyFCXCpkJHpEc2I9
    username: YWRtaW4=
    kind: Secret
    metadata:
    creationTimestamp: "2022-06-28T17:44:13Z"
    name: db-user-pass
    namespace: default
    resourceVersion: "12708504"
    uid: 91becd59-78fa-4c85-823f-6d44436242ac
    type: Opaque
    ```