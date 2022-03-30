### Photonix Demo
  https://photonix.org/?fbclid=IwAR05GHoBsG7jTrS1oit4yjKzjtTSSUZh-TEdB4utJf0JWQJdd3gu7xmcBW0


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
helm install minio  bitnami/minio -n minio --create-namespace --set auth.rootPassword=Shlonski2712
```

- [ ] install rabbitmq

```
helm install rabbitmq bitnami/rabbitmq -n rabbit --create-namespace --set auth.password=pass
```

- [ ] install mongodb

```
helm install mongodb bitnami/mongodb -n mongodb --create-namespace --set auth.rootPassword=pass
```

- [ ] expose all services

```
//minio
kubectl patch svc minio -p '{"spec": { "type": "NodePort", "ports": [ {"port":9000, "nodePort": 30010 },{"port":9001, "nodePort": 30011 } ] } }' -n minio

//rabbitmq
kubectl patch svc rabbitmq -p '{"spec": { "type": "NodePort", "ports": [ {"port":15672, "nodePort": 30005 },{"port":5672, "nodePort": 30004 } ] } }' -n rabbit

//mongodb
kubectl patch svc mongodb -p '{"spec": { "type": "NodePort", "ports": [ {"port":27017, "nodePort": 30015 } ] } }' -n mongodb

//argo
kubectl patch svc argo-server -p '{"spec": { "type": "NodePort", "ports": [ {"port":2746, "nodePort": 30001 } ] } }' -n argo-events

```

- [ ] install argo-events

```
kubectl create namespace argo-events
kubectl apply -f https://raw.githubusercontent.com/argoproj/argo-events/stable/manifests/install.yaml
# Install with a validating admission controller
kubectl apply -f https://raw.githubusercontent.com/argoproj/argo-events/stable/manifests/install-validating-webhook.yaml
#setup the event buss
kubectl apply -n argo-events -f https://raw.githubusercontent.com/argoproj/argo-events/stable/examples/eventbus/native.yaml
```

- [ ] setup minio or use argo's
  - [ ] check mc connection & create bucket

```
./mc alias set minio/ http://localhost:30010 admin Shlonski2712
./mc mb minio/new-files
./mc policy set public minio/new-files
./mc mb minio/photos
./mc policy set public minio/photos
./mc mb minio/thumbnails-todo
./mc policy set public minio/thumbnails-todo
./mc mb minio/thumbnails
./mc policy set public minio/thumbnails
./mc ls minio
```

- [ ] check ui connection - http://localhost:30011
- [ ] setup rabbit message on add file

  - [ ] check ui connection - localhost:30005
  - [ ] create rabbit exchange for files events

    ```
      //get rabbitmqadmin -cli
      wget http://127.0.0.1:30005/cli/rabbitmqadmin
      chmod +x rabbitmqadmin

    //create exchange + queue and bind them
    ./rabbitmqadmin -H localhost -P 30005 -u user  -p pass declare exchange  name=new-file type=direct durable=false
    ./rabbitmqadmin -H localhost -P 30005 -u user  -p pass declare queue  name=new-files durable=true
    ./rabbitmqadmin -H localhost -P 30005 -u user  -p pass declare binding source="new-file" destination_type="queue" destination="new-files" routing_key="new-file"
    ```

    - [ ] setup minio - endpoint notification - AMQP

    ```
      ./mc admin config set minio notify_amqp:rabbitmq url="amqp://user:pass@rabbitmq.rabbit.svc.cluster.local:5672" exchange="new-file" exchange_type="direct" durable="false" routing_key="new-file"
      ./mc admin service restart minio
    ```

    - [ ] setup minio - set bucket notification

    ```
      ./mc event add minio/new-files arn:minio:sqs::rabbitmq:amqp  --event put
    ```

- [ ] setup argo-workflows to handle new file

  - [ ] setup an event source for new files
  ```
    kubectl apply -f ./k8s-yaml/amqp-yaml/argo-amqp-eventsource.yaml -n argo-events
  ```
  - [ ] configure a service account to handle the event
  ```
    //create service account
    kubectl -n argo-events create sa argo-sensor-sa
    //create a cluster-role (this case cluster wide)
    kubectl create clusterrole deployments-watcher --verb=list,watch,create,update,get --resource=deployments.apps,pods,workflows.argoproj.io
    //bind the cluster role to the service account
    kubectl create clusterrolebinding deployments-watcher-clusterrole-binding --clusterrole=deployments-watcher --serviceaccount=argo-events:argo-sensor-sa
  ```
  - [ ] deploy the event sensor
  ```
    kubectl apply  -f ./k8s-yaml/amqp-yaml/argo-amqp-sensor.yaml  -n argo-events
  ```
