- [x] setup  k3d cluster
```
 k3d cluster create argo-wf --api-port 6550 -p "30000-30080:30000-30080@server:0" --agents 2 
```
- [ ]  install & configure argo-workflows, minio and rabbitmq on k3d
  - [ ]  install argo-workflows
  - [ ]  install minio
```
helm install minio  bitnami/minio -n minio --create-namespace
```
  - [ ]  install rabbitmq
```
helm install rabbitmq bitnami/rabbitmq -n rabbit --create-namespace
```
  - [ ]  expose all services
```
kubectl get svc -n minio
kubectl edit svc minio -n minio
```
- [ ] setup minio or use argo's
  - [ ] check mc connection 
```
mc alias set minio/ http://localhost:30002 <user> <password>
mc ls /minio 
```
  - [ ] check ui connection
- [ ] setup argo event on file drop
  - [ ]  check input
  - [ ] check output handling - needs to be able to drop to different bucket - and handle db logging