# 离线包资源记录

离线包已经覆盖 MPI 和监控系统继续推进所需的核心资源，但不包含云账号信息、SWR 登录信息、KubeConfig、CI/CD Secrets，也没有 PyTorch DDP 训练镜像。

## MPI 方向

已有文件：

```text
离线包/mpi/mpi4py-latest.tar
离线包/mpi/mpi-operator.yaml
```

使用顺序：

```bash
cd /mnt/d/vsCode/python/yjs/离线包
docker load -i mpi/mpi4py-latest.tar

SWR="swr.<region>.myhuaweicloud.com/<your-organization>"
docker tag swr.cn-east-3.myhuaweicloud.com/cloud-course-2025212245/mpi4py:latest ${SWR}/mpi4py:latest
docker push ${SWR}/mpi4py:latest

kubectl apply -f mpi/mpi-operator.yaml
```

如果用仓库里的 `mpi/Dockerfile`，可以构建带本项目脚本的镜像：

```bash
docker build -t yjs-mpi:v1 -f mpi/Dockerfile mpi
docker tag yjs-mpi:v1 ${SWR}/yjs-mpi:v1
docker push ${SWR}/yjs-mpi:v1
```

## 监控系统

已有文件：

```text
离线包/monitoring/monitoring-all.tar
离线包/monitoring/kube-prometheus-stack-83.7.0.tgz
离线包/monitoring/monitoring-values.yaml
```

需要先加载镜像、重新 tag 到个人 SWR、推送，再用 Helm 安装。仓库里保留了 `deploy/k8s/monitoring/monitoring-values.template.yaml`，替换 `<region>` 和 `<your-organization>` 后使用。

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

- 华为云 Region。
- SWR 组织名。
- SWR 登录命令或临时 Token。
- CCE KubeConfig。
- GitHub Actions Secrets。
- ELB 公网 IP。
- 云上截图和运行日志。
