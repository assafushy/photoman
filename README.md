- [x] setup k3d cluster

```
 k3d cluster create argo-wf --api-port 6550 -p "30000-30080:30000-30080@server:0" --agents 2

cat ~/.kube/config
```

- [ ] install & configure argo-workflows, minio and rabbitmq on k3d
  - [ ] install argo-workflows

```
kubectl create ns argo-events
kubectl apply -n argo-events -f https://raw.githubusercontent.com/argoproj/argo-workflows/master/manifests/quick-start-postgres.yaml
```

- [ ] install minio

```
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install minio  bitnami/minio -n minio --create-namespace
```

- [ ] install rabbitmq

```
helm install rabbitmq bitnami/rabbitmq -n rabbit --create-namespace
```

- [ ] expose all services

```
//minio
kubectl patch svc minio -p '{"spec": { "type": "NodePort", "ports": [ {"port":9000, "nodePort": 30010 },{"port":9001, "nodePort": 30011 } ] } }' -n minio

//rabbitmq
kubectl patch svc rabbitmq -p '{"spec": { "type": "NodePort", "ports": [ {"port":15672, "nodePort": 30005 },{"port":5672, "nodePort": 30004 } ] } }' -n rabbit

//argo
kubectl patch svc argo-server -p '{"spec": { "type": "NodePort", "ports": [ {"port":2746, "nodePort": 30001 } ] } }' -n argo-events

```

- [ ] install argo-events

```
kubectl create namespace argo-events
kubectl apply -f https://raw.githubusercontent.com/argoproj/argo-events/stable/manifests/install.yaml
# Install with a validating admission controller
kubectl apply -f https://raw.githubusercontent.com/argoproj/argo-events/stable/manifests/install-validating-webhook.yaml
```

- [ ] setup minio or use argo's
  - [ ] check mc connection & create bucket

```
./mc alias set minio/ http://localhost:30010 <user> <password>
./mc ls minio
./mc mb minio new-files
./mc policy set public minio/new-files
```

- [ ] check ui connection - localhost:30011
- [ ] setup rabbit message on add file

  - [ ] create rabbit exchange for files events

    ```
      //get rabbitmqadmin -cli
      wget http://127.0.0.1:30005/cli/rabbitmqadmin
      chmod +x rabbitmqadmin

    //create exchange + queue and bind them
    ./rabbitmqadmin declare exchange -H localhost -P 30005 -u user  -p lKMQihjCT7 name=new-file type=direct
    ./rabbitmqadmin declare queue -H localhost -P 30005 -u user  -p lKMQihjCT7  name=new-files durable=true
    ./rabbitmqadmin -H localhost -P 30005 -u user  -p lKMQihjCT7 declare binding source="new-file" destination_type="queue" destination="new-files"
    ```

    - [ ] setup minio - endpoint notification - AMQP

    ```
          ./mc admin config set minio notify_amqp:rabbitmq url="amqp://user:lKMQihjCT7@rabbitmq.rabbit.svc.cluster.local:5672" exchange="new-file" exchange_type="direct" durable="false"
          ./mc admin service restart minio
    ```

    - [ ] setup minio - set bucket notification

    ```
      ./mc event add minio/new-files arn:minio:sqs::rabbitmq:amqp  --event put
    ```

- [ ] setup argo-workflows to handle new file

```

```
