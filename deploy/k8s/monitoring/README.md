# 监控系统部署 notes

这里不放离线镜像包，只保留部署时需要修改的小文件和命令。

离线包位置：

```text
离线包/monitoring/kube-prometheus-stack-83.7.0.tgz
离线包/monitoring/monitoring-all.tar
离线包/monitoring/monitoring-values.yaml
```

部署前先在 WSL 里把离线镜像加载、重新打 tag，并推到自己的 SWR：

```bash
cd /mnt/d/vsCode/python/yjs/离线包
docker load -i monitoring/monitoring-all.tar

SWR="swr.<region>.myhuaweicloud.com/<your-organization>"
OLD="swr.cn-east-3.myhuaweicloud.com/cloud-course-2025212245"

docker tag ${OLD}/grafana:12.4.3 ${SWR}/grafana:12.4.3
docker tag ${OLD}/k8s-sidecar:2.6.0 ${SWR}/k8s-sidecar:2.6.0
docker tag ${OLD}/prometheus:v3.11.2 ${SWR}/prometheus:v3.11.2
docker tag ${OLD}/alertmanager:v0.32.0 ${SWR}/alertmanager:v0.32.0
docker tag ${OLD}/prometheus-operator:v0.90.1 ${SWR}/prometheus-operator:v0.90.1
docker tag ${OLD}/kube-webhook-certgen:1.8.1 ${SWR}/kube-webhook-certgen:1.8.1
docker tag ${OLD}/prometheus-config-reloader:v0.90.1 ${SWR}/prometheus-config-reloader:v0.90.1
docker tag ${OLD}/node-exporter:v1.11.1 ${SWR}/node-exporter:v1.11.1
```

登录并推送后，把 `monitoring-values.template.yaml` 里的 `<region>` 和 `<your-organization>` 替换成真实值，再安装：

```bash
helm upgrade --install monitoring 离线包/monitoring/kube-prometheus-stack-83.7.0.tgz \
  -n monitoring --create-namespace \
  -f deploy/k8s/monitoring/monitoring-values.template.yaml
```

截图建议：

- `helm list -n monitoring`
- `kubectl get pods -n monitoring`
- Grafana 节点 CPU 利用率折线图
- Grafana 各 Pod 内存使用柱状图
