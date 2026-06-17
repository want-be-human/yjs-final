# 离线包资源记录

离线包已经覆盖 MPI 和监控系统继续推进所需的核心资源，但不包含云账号信息、SWR 登录信息、KubeConfig、CI/CD Secrets，也没有 PyTorch DDP 训练镜像。

## 已确认云资源

```text
Region: cn-north-4（华北-北京四）
SWR Registry: swr.cn-north-4.myhuaweicloud.com
SWR Organization: yjs-final-2023112473
CCE Cluster: yjs-final-cluster
Kubernetes Version: v1.35.3-r0-35.0.8
Worker Nodes: 3 个，Ubuntu 22.04，containerd
```

前后端镜像已经推送到 SWR：

```text
swr.cn-north-4.myhuaweicloud.com/yjs-final-2023112473/yjs-backend:v1
swr.cn-north-4.myhuaweicloud.com/yjs-final-2023112473/yjs-frontend:v1
swr.cn-north-4.myhuaweicloud.com/yjs-final-2023112473/yjs-mpi:v2
```

普通 `docker push` 后端镜像时曾遇到 `Invalid image, fail to parse 'manifest.json'`，后续使用兼容命令重新构建并推送：

```bash
docker buildx build \
  --platform linux/amd64 \
  --provenance=false \
  -t swr.cn-north-4.myhuaweicloud.com/yjs-final-2023112473/yjs-backend:v1 \
  -f app/backend/Dockerfile.backend app/backend \
  --push
```

## MPI 方向

已有文件：

```text
离线包/mpi/mpi-operator.yaml
```

实际使用顺序：

```bash
cd /mnt/d/desktop/云计算/yjs-final

SWR="swr.cn-north-4.myhuaweicloud.com/yjs-final-2023112473"
docker buildx build \
  --platform linux/amd64 \
  --provenance=false \
  --push \
  -t ${SWR}/yjs-mpi:v2 \
  -f mpi/Dockerfile mpi

kubectl apply -f 离线包/mpi/mpi-operator.yaml
kubectl apply -f deploy/k8s/mpi/mpijob.yaml
```

MPIJob 运行中处理过的问题：

- MPI Operator CRD 使用 `kubeflow.org/v2beta1`，因此仓库里的 MPIJob YAML 已改为该版本。
- SWR 普通 push 曾出现 manifest 解析问题，统一使用 `docker buildx build --platform linux/amd64 --provenance=false --push`。
- MPI Worker 需要 `/usr/sbin/sshd`，镜像中已加入 `openssh-server`。
- OpenMPI 在容器 root 用户下运行需要 `--allow-run-as-root`。
- CCE 小规格节点上可用 slot 不足时，`mpirun` 增加 `--oversubscribe`。

已保存截图：

- `docs/screenshots/cce-mpi-operator-running.png`
- `docs/screenshots/cce-mpijob-pods-completed.png`
- `docs/screenshots/cce-mpijob-job-complete.png`
- `docs/screenshots/cce-mpijob-pi-log.png`

## 监控系统

已有文件：

```text
离线包/monitoring/monitoring-all.tar
离线包/monitoring/kube-prometheus-stack-83.7.0.tgz
离线包/monitoring/monitoring-values.yaml
```

需要先加载镜像、重新 tag 到个人 SWR、推送，再用 Helm 安装。仓库里保留了 `deploy/k8s/monitoring/monitoring-values.template.yaml`，后续需要把 `<region>` 替换为 `cn-north-4`，把 `<your-organization>` 替换为 `yjs-final-2023112473` 后使用。

```bash
helm upgrade --install monitoring 离线包/monitoring/kube-prometheus-stack-83.7.0.tgz \
  -n monitoring --create-namespace \
  -f deploy/k8s/monitoring/monitoring-values.template.yaml
```

报告里要放：

- Prometheus + Grafana 部署成功截图。
- Grafana 节点 CPU 利用率折线图。
- Grafana 各 Pod 内存使用柱状图。
- Prometheus Pull 采集原理。
- 至少 3 个指标含义。

## Spark 方向

离线包也有 Spark Operator 和 PySpark 镜像，但当前课程设计选择的是 MPI 方向，不作为主线使用。

```text
离线包/spark/spark-operator-2.5.0.tar
离线包/spark/pyspark-v9.tar
离线包/spark/spark-operator/
```

## 仍然缺的真实信息

- SWR 登录命令或临时 Token（仅本地使用，不提交）。
- GitHub Actions Secrets。
- 监控和 CI/CD 的云上截图及运行日志。
