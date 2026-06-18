# 云计算技术课程设计实验报告

## 封面

课程名：云计算技术  
学号：2023112473  
姓名：谢梦瑶  
班级：待补充  
日期：2026 年 6 月 17 日  

代码仓库：`https://github.com/want-be-human/yjs-final`

## 华为云环境信息

本次实验运行环境以 WSL 为准，Windows 只作为编辑环境。云资源部署在华为云华北-北京四区，镜像统一推送到 SWR 组织 `yjs-final`，Kubernetes 集群为 CCE 集群 `yjs-final-cluster`。

| 项目 | 当前值 |
|---|---|
| Region | `cn-north-4` |
| SWR Registry | `swr.cn-north-4.myhuaweicloud.com` |
| SWR Organization | `yjs-final` |
| CCE 集群 | `yjs-final-cluster` |
| Kubernetes 版本 | `v1.35.3-r0-35.0.8` |
| Worker 节点 | 3 个，前 2 个为 2 vCPU / 4 GiB，后续因 HPA 和监控组件资源不足新增 1 个 2 vCPU / 8 GiB 节点 |
| 后端公网入口 | `http://114.116.194.77/api/ping` |

![CCE 节点状态](screenshots/2.3-cce-nodes-ready-version.png)

> 待补截图：CCE 控制台集群概览截图，建议包含集群名称、版本、节点数量和 Region。

## 第一部分：云计算平台搭建

第一部分部署的是一套 `Flask 后端 API + Redis 数据库 + Nginx 前端页面` 的两层 Web 应用。后端提供 `/api/ping` 和 `/api/info` 接口，其中 `/api/ping` 会连接 Redis 并累计访问次数；前端由 Nginx 提供静态页面，并通过反向代理访问后端接口。所有部署文件都放在 `deploy/k8s/app/` 下，核心应用代码放在 `app/backend/` 和 `app/frontend/` 下。

### 任务 1：应用容器化

本任务完成了后端和前端镜像构建。后端 `Dockerfile.backend` 保留多阶段构建结构，依赖文件 `requirements.txt` 中包含 `flask`、`redis` 和自选包 `requests`。前端 `Dockerfile.frontend` 基于 Nginx 镜像，将 `static/index.html` 和 Nginx 配置复制进容器。  

本地联调使用 `docker-compose.yml` 启动 `frontend`、`backend` 和 `redis` 三个服务。前端映射到本机 `8080` 端口，后端映射到 `5000` 端口。验证时先启动 compose，再访问前端页面，点击按钮触发 `/api/ping`，同时查看后端日志确认请求已经到达 Flask 服务。

操作步骤摘要：

```bash
docker compose up --build -d
docker compose ps
docker compose logs --tail=80 backend
curl http://localhost:8080/api/ping
curl http://localhost:5000/api/info
```

关键截图：

![本地前端访问后端接口](screenshots/2.2-local-frontend-api-result.png)

![本地后端日志](screenshots/2.2-local-backend-log.png)

> 待补截图：当前 `yjs-final` 组织下 `yjs-backend` 和 `yjs-frontend` 镜像 Tag 页面。旧组织名截图不要使用。

问题与解决方案：  
普通 `docker push` 在华为云 SWR 上曾遇到 manifest 解析问题，后续镜像统一按 Linux amd64 平台构建并推送。GitHub Actions 中也使用同样的 Dockerfile 路径构建前后端镜像，避免本地和流水线构建上下文不一致。

### 任务 2：CCE 集群搭建

本任务在华为云 CCE 中创建 Kubernetes 集群，集群版本满足任务书要求的 `>= 1.27`。实际使用版本为 `v1.35.3-r0-35.0.8`。实验初期使用两个 Worker 节点，后续因为 metrics-server、HPA 压测和监控组件调度需要，新增了一个 2 vCPU / 8 GiB Worker 节点。

操作步骤摘要：

```bash
export KUBECONFIG=/mnt/d/vsCode/python/yjs/yjs-final-cluster-kubeconfig.yaml
kubectl get nodes -o wide
```

关键截图：

![CCE 节点 Ready 和版本信息](screenshots/2.3-cce-nodes-ready-version.png)

问题与解决方案：  
KubeConfig 文件只保存在本地，不提交到仓库。仓库 `.gitignore` 已忽略 `yjs-final-cluster-kubeconfig.yaml`、`kubeconfig*.yaml`、证书和本地配置文件。WSL 是实际运行环境，Windows 只用于编辑，避免路径和命令差异影响实验复现。

### 任务 3：应用部署

本任务将前后端和 Redis 部署到 CCE。后端 Deployment 名为 `backend`，副本数为 2，镜像来自 SWR；Redis Deployment 名为 `redis`，副本数为 1；前端 Deployment 名为 `frontend`。后端 Service `backend-svc` 使用 `LoadBalancer` 类型并带有华为云 ELB 注解，Redis Service 使用 `ClusterIP`，只在集群内部访问。

操作步骤摘要：

```bash
kubectl apply -f deploy/k8s/app/configmap.yaml
kubectl apply -f deploy/k8s/app/secret.yaml
kubectl apply -f deploy/k8s/app/redis-pvc.yaml
kubectl apply -f deploy/k8s/app/redis-deployment.yaml
kubectl apply -f deploy/k8s/app/deployment.yaml
kubectl apply -f deploy/k8s/app/frontend-deployment.yaml
kubectl apply -f deploy/k8s/app/service.yaml
kubectl get deployment
kubectl get pods -o wide
kubectl get svc
curl http://114.116.194.77/api/ping
```

关键截图：

![应用 Deployment 状态](screenshots/2.4-app-deployments-ready.png)

![应用 Pod 状态](screenshots/2.4-app-pods-running-wide.png)

> 待补截图：当前 `kubectl get svc`，必须显示当前后端 ELB `114.116.194.77`。  
> 待补截图：当前 `curl http://114.116.194.77/api/ping` 返回结果，必须包含 `redis: ok`。

问题与解决方案：  
最初 Service YAML 中曾绑定具体 ELB ID。这样做会让 YAML 和单个历史 ELB 强绑定，换账号或重建集群后容易失败。后续已移除固定 `kubernetes.io/elb.id`，只保留 `kubernetes.io/elb.class: union`，由当前集群按环境绑定 ELB。

### 任务 4：持久化存储

Redis 通过 PVC 持久化 `/data` 目录，PVC 名称为 `redis-data-pvc`，StorageClass 使用华为云 `csi-disk`。Redis Deployment 使用 `Recreate` 策略，避免同一块云硬盘被新旧 Pod 同时挂载。

操作步骤摘要：

```bash
kubectl get pvc
REDIS_POD=$(kubectl get pod -l app=redis -o jsonpath='{.items[0].metadata.name}')
kubectl exec "$REDIS_POD" -- redis-cli -a cloudredis123 SET testkey "hello-pvc"
kubectl exec "$REDIS_POD" -- redis-cli -a cloudredis123 GET testkey
kubectl delete pod "$REDIS_POD"
kubectl wait --for=condition=Ready pod -l app=redis --timeout=180s
NEW_REDIS_POD=$(kubectl get pod -l app=redis -o jsonpath='{.items[0].metadata.name}')
kubectl exec "$NEW_REDIS_POD" -- redis-cli -a cloudredis123 GET testkey
```

关键截图：

![Redis PVC Bound](screenshots/2.5-redis-pvc-bound.png)

![Redis 写入并读取 key](screenshots/2.5-redis-set-get-before-delete.png)

![删除 Redis Pod 后重建](screenshots/2.5-redis-pod-recreated.png)

![重建后仍可读取 key](screenshots/2.5-redis-get-after-recreate.png)

问题与解决方案：  
Redis 使用密码保护，验证时命令中会出现 `redis-cli -a` 的安全提示。报告只展示课程测试密码，不展示云账号、SWR token、KubeConfig 或 AK/SK。持久化验证重点不是 Redis 进程本身，而是 Pod 删除重建后数据仍然保留。

### 任务 5：ConfigMap Volume 挂载

本任务将 Nginx 反向代理配置从镜像内文件改成 ConfigMap Volume 挂载。`frontend-nginx-config` ConfigMap 中保存完整 `default.conf`，前端 Deployment 将其挂载到 `/etc/nginx/conf.d`。这种方式适合完整配置文件，比 `envFrom` 更适合 Nginx 这类按文件读取配置的程序。

操作步骤摘要：

```bash
kubectl apply -f deploy/k8s/app/nginx-configmap.yaml
FRONTEND_POD=$(kubectl get pod -l app=frontend -o jsonpath='{.items[0].metadata.name}')
kubectl exec "$FRONTEND_POD" -- cat /etc/nginx/conf.d/default.conf
```

关键截图：

![ConfigMap Volume 挂载内容](screenshots/2.6-configmap-volume-mounted.png)

![ConfigMap 更新后容器内文件同步](screenshots/2.6-configmap-volume-updated.png)

问题与解决方案：  
配置更新后并不是所有应用都会自动 reload。Nginx 配置文件可以在容器内看到更新，但正式变更代理行为时仍应按需要 reload 或重启前端 Pod。本实验重点验证 Volume 挂载和文件同步，因此通过 `kubectl exec cat` 验证文件内容。

### 任务 6：HPA 弹性伸缩

本任务为后端 Deployment 配置 HPA，`minReplicas=1`，`maxReplicas=4`，CPU 目标利用率为 60%。压测时使用 BusyBox Pod 持续请求 `backend-svc/api/ping`，观察后端副本扩容；停止压测后等待 HPA 缩容。

操作步骤摘要：

```bash
kubectl top nodes
kubectl apply -f deploy/k8s/app/backend-hpa.yaml
kubectl get hpa
kubectl run load-generator-1 --image=busybox:1.36 --restart=Never -- /bin/sh -c "while true; do wget -q -O- http://backend-svc/api/ping >/dev/null; done"
kubectl run load-generator-2 --image=busybox:1.36 --restart=Never -- /bin/sh -c "while true; do wget -q -O- http://backend-svc/api/ping >/dev/null; done"
kubectl run load-generator-3 --image=busybox:1.36 --restart=Never -- /bin/sh -c "while true; do wget -q -O- http://backend-svc/api/ping >/dev/null; done"
kubectl get hpa
kubectl get pods
kubectl delete pod load-generator-1 load-generator-2 load-generator-3 --ignore-not-found
```

关键截图：

![metrics-server 指标可用](screenshots/2.7-hpa-metrics-top-nodes.png)

![HPA 创建成功](screenshots/2.7-hpa-created.png)

![压测后扩容到 4 个副本](screenshots/2.7-hpa-scale-up-to-4.png)

![停止压测后缩容](screenshots/2.7-hpa-scale-down.png)

问题与解决方案：  
HPA 扩容不是实时发生，原因包括 metrics-server 采集周期、HPA 控制器评估间隔和 Pod 调度耗时。缩容也不会马上执行，冷却时间可以避免短时间负载波动造成频繁扩缩容。实验中一开始节点资源不足导致指标组件调度不稳定，后续新增 Worker 节点后，`kubectl top nodes` 能返回数据，HPA 才能正常工作。

## 第二部分：方向 B，MPI 并行科学计算

第二部分选择方向 B：MPI 并行科学计算。算法题选择数值积分（梯形法），目标是计算：

```text
pi = integral(0, 1, 4 / (1 + x^2)) dx
```

代码位于 `mpi/` 目录。串行版本为 `integral_serial.py`，阻塞 MPI 版本为 `integral_mpi.py`，非阻塞版本为 `integral_mpi_nonblocking.py`，性能测试脚本为 `bench_mpi.py`，Amdahl 图生成脚本为 `plot_amdahl.py`。

### B-0：MPI 环境部署

本任务使用老师提供的 MPI Operator 和 `mpi4py:latest` 离线镜像。镜像重新 tag 到个人 SWR 后，MPIJob 使用 `kubeflow.org/v2beta1`，`slotsPerWorker=2`，`Worker replicas=2`，总进程数为 4。

操作步骤摘要：

```bash
kubectl apply -f 离线包/mpi/mpi-operator.yaml
kubectl get pods -n mpi-operator
kubectl create configmap mpi-scripts \
  --from-file=mpi/pi_mpi.py \
  --from-file=mpi/integral_mpi.py \
  --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -f deploy/k8s/mpi/mpijob.yaml
kubectl get mpijob
kubectl get jobs
kubectl logs job/mpi-pi-launcher
```

关键截图：

![MPI Operator Running](screenshots/3.3-B-0-mpi-operator-running.png)

![MPIJob Job Complete](screenshots/3.3-B-0-mpijob-job-complete.png)

![MPI pi 示例日志](screenshots/3.3-B-0-mpijob-pi-log.png)

![MPIJob Pod 和 Job 状态](screenshots/3.3-B-0-mpijob-pods-and-job.png)

问题与解决方案：  
MPI Operator 的 CRD 版本和模板示例不完全一致，实际集群使用 `kubeflow.org/v2beta1`。另外，老师镜像保持不重打包，项目脚本通过 `mpi-scripts` ConfigMap 挂载到 `/opt/mpi`，这样既保留老师镜像，也能运行自己的 Python 程序。

### B-1：并行算法实现

串行版将 `[0, 1]` 区间均匀切分为固定步数，用梯形法累加面积。MPI 阻塞版先由 rank 0 计算每个进程负责的区间片段，再通过 `comm.scatter` 分发 `(start_index, count)`，每个进程计算局部积分后通过 `comm.reduce` 汇总到 rank 0。代码中已对 `scatter` 和 `reduce` 的数据流向做了注释。

通信模式如下：

```text
rank 0
  |
  | scatter: 分发每个进程负责的起点和区间数量
  v
rank 0     rank 1     rank 2     rank 3
  |          |          |          |
  | 本地累加 | 本地累加 | 本地累加 | 本地累加
  |          |          |          |
  +----------+----------+----------+
             reduce: partial sum 汇总回 rank 0
```

关键截图：

![串行和 MPI 并行结果一致](screenshots/3.3-B-1-serial-vs-mpi-consistency.png)

结果示例：

```text
method=mpi-blocking processes=4 steps=10000000 pi=3.141592653590 error=1.066e-14
```

结果与圆周率参考值一致，误差在 `1e-14` 量级。

### B-2：性能测试与 Amdahl 分析

性能测试固定问题规模为 `steps=10000000`，分别使用 1、2、4 个 MPI 进程运行，每种进程数运行 3 次并取平均。测试数据如下：

| 进程数 | 三次运行时间 / s | 平均时间 / s | 实测加速比 | Amdahl 理论值 |
|---:|---|---:|---:|---:|
| 1 | 0.718948, 0.776388, 0.807686 | 0.767674 | 1.000000 | 1.000000 |
| 2 | 0.380760, 0.383996, 0.375098 | 0.379951 | 2.020453 | 1.930346 |
| 4 | 0.212183, 0.194609, 0.231290 | 0.212694 | 3.609288 | 3.609288 |

按 4 进程实测加速比反推，可并行比例约为 `0.9639`。4 进程加速比较明显，但没有达到理想线性加速，主要原因是进程启动、任务分发、Reduce 汇总和同步仍然存在固定开销。

关键截图：

![MPI 性能测试日志](screenshots/3.3-B-2-benchmark-log.png)

![Amdahl 加速比曲线](screenshots/3.3-B-2-amdahl-speedup.png)

### B-3：非阻塞通信优化

非阻塞版本没有继续使用 `scatter/reduce`，而是由 rank 0 使用 `Isend` 给 worker 发送任务，再使用 `Irecv` 提前挂起结果接收。rank 0 在等待 worker 返回之前先计算自己的分片，从结构上体现计算和通信的重叠。

本次 4 进程对比结果中，非阻塞版本并不一定更快。原因是当前任务每个进程只接收一次区间、返回一次局部积分，通信量很小，可重叠的通信时间有限；非阻塞版本还引入了更多点对点请求管理开销。非阻塞通信更适合通信延迟较高、通信和计算能明显重叠、迭代次数较多的场景。

关键截图：

![阻塞和非阻塞通信对比](screenshots/3.3-B-3-blocking-vs-nonblocking.png)

## 附加题实验记录

### 附加题 1：监控系统

监控系统一开始按任务书尝试使用离线包中的 `kube-prometheus-stack-83.7.0.tgz` 部署完整 Prometheus + Grafana。实际部署时，CCE 集群中已有旧版 Prometheus Operator CRD，新版 Chart 渲染出的部分 Prometheus/Operator 字段无法被当前 CRD 正常接受。直接覆盖 CRD 风险较高，可能影响集群已有监控 CRD 和后续资源创建，因此最终没有强行替换集群 CRD。

最终方案为：仍使用 kube-prometheus-stack 部署 Grafana 页面和 Dashboard，自建 `yjs-prometheus` Deployment 采集集群指标，再将 Grafana datasource 指向 `http://yjs-prometheus.monitoring:9090/`。这个方案保留了 Prometheus Pull 采集和 Grafana 可视化两个核心环节，但它不是完整 Chart 原样部署成功，报告中需要如实说明。

操作步骤摘要：

```bash
helm upgrade --install yjs-monitoring 离线包/monitoring/kube-prometheus-stack-83.7.0.tgz \
  -n monitoring --create-namespace \
  -f deploy/k8s/monitoring/monitoring-values.yaml

kubectl apply -f deploy/k8s/monitoring/yjs-prometheus.yaml
kubectl apply -f deploy/k8s/monitoring/grafana-datasource.yaml
helm list -n monitoring
kubectl get pods -n monitoring
kubectl -n monitoring port-forward svc/yjs-prometheus 9090:9090
kubectl -n monitoring port-forward svc/yjs-monitoring-grafana 3000:80
```

代码说明：  
`monitoring-values.yaml` 中关闭了完整 Chart 的 Prometheus Operator 和内置 Prometheus，保留 Grafana。`yjs-prometheus.yaml` 创建 ServiceAccount、RBAC、配置文件、Prometheus Deployment 和 Service，采集 node-exporter、kube-state-metrics 和 kubelet cAdvisor 指标。`grafana-datasource.yaml` 通过 ConfigMap 将 Grafana datasource 指向自建 Prometheus。

Prometheus Pull 采集原理：  
Prometheus 不要求业务主动上报指标，而是按配置中的 target 定时访问 `/metrics` 接口。每次抓取结果会记录到时间序列数据库中，指标通过标签区分节点、Pod、容器和命名空间。Grafana 不直接采集指标，只负责向 Prometheus 查询并展示图表。报告中选取 `node_cpu_seconds_total`、`container_memory_working_set_bytes`、`container_cpu_usage_seconds_total` 和 `up` 作为说明指标。

关键截图：

> 待补截图：`4.1-monitoring-helm-list.png`，展示 `helm list -n monitoring`。  
> 待补截图：`4.1-monitoring-pods-running.png`，展示 `kubectl get pods -n monitoring`。  
> 待补截图：`4.1-prometheus-node-cpu-query.png`，展示 Prometheus 查询 `node_cpu_seconds_total`。  
> 待补截图：`4.1-prometheus-pod-memory-query.png`，展示 Prometheus 查询 `container_memory_working_set_bytes`。  
> 待补截图：`4.1-grafana-node-cpu-line.png`，展示 Grafana 节点 CPU 折线图。  
> 待补截图：`4.1-grafana-pod-memory-bar.png`，展示 Grafana Pod 内存柱状图。

问题与解决方案：  
完整 Chart 原样部署受 CCE 现有 CRD 版本影响。为避免破坏集群已有 CRD，采用 Grafana + 自建 Prometheus 的替代方案，并通过 Prometheus 查询和 Grafana datasource 验证采集链路可用。

### 附加题 2：CI/CD 流水线

CI/CD 使用 GitHub Actions 实现。流程为：代码提交或手动触发 workflow 后，Actions 自动构建前端和后端镜像，登录华为云 SWR，推送镜像到 `yjs-final` 组织，然后通过 KubeConfig 更新 CCE 中的 `backend` 和 `frontend` Deployment 镜像 Tag。

workflow 文件为 `.github/workflows/deploy.yml`。敏感信息全部通过 GitHub Repository Secrets 注入，包括 `SWR_REGISTRY`、`SWR_ORG`、`SWR_USERNAME`、`SWR_PASSWORD` 和 `KUBE_CONFIG`，没有写入仓库。

操作步骤摘要：

```bash
# GitHub Actions 自动执行，核心步骤如下：
docker login "$SWR_REGISTRY"
docker build -t "$SWR_REGISTRY/$SWR_ORG/yjs-backend:$IMAGE_TAG" -f app/backend/Dockerfile.backend app/backend
docker build -t "$SWR_REGISTRY/$SWR_ORG/yjs-frontend:$IMAGE_TAG" -f app/frontend/Dockerfile.frontend app/frontend
docker push "$SWR_REGISTRY/$SWR_ORG/yjs-backend:$IMAGE_TAG"
docker push "$SWR_REGISTRY/$SWR_ORG/yjs-frontend:$IMAGE_TAG"
kubectl set image deployment/backend backend="$SWR_REGISTRY/$SWR_ORG/yjs-backend:$IMAGE_TAG"
kubectl set image deployment/frontend frontend="$SWR_REGISTRY/$SWR_ORG/yjs-frontend:$IMAGE_TAG"
kubectl rollout status deployment/backend --timeout=180s
kubectl rollout status deployment/frontend --timeout=180s
```

代码说明：  
workflow 中 `IMAGE_TAG` 使用 GitHub commit SHA 前 7 位，能把每次部署和代码提交关联起来。`Configure kubectl` 步骤把 base64 后的 KubeConfig 解码到 runner 的 `$HOME/.kube/config`，只在流水线运行时使用。`Update deployments` 步骤通过 `kubectl set image` 更新镜像，并等待 rollout 成功。

关键截图：

![GitHub Actions 流水线截图 1](screenshots/流水线截图1.png)

![GitHub Actions 流水线截图 2](screenshots/流水线截图2.png)

> 待补截图：`4.2-swr-backend-new-tag.png`，展示 SWR 后端新 tag。  
> 待补截图：`4.2-swr-frontend-new-tag.png`，展示 SWR 前端新 tag。  
> 待补截图：`4.2-k8s-deployment-image-updated.png`，展示 `kubectl get deployment backend frontend -o wide` 中镜像 Tag 已更新。  
> 待补截图：`4.2-api-ping-after-cicd.png`，展示流水线后 `/api/ping` 仍可访问。

问题与解决方案：  
第一次运行流水线时在 `docker login` 步骤出现过 `denied: Authenticate Error`。定位后确认问题发生在 SWR 认证阶段，不是 Dockerfile、构建上下文或 KubeConfig。后续按华为云 SWR 控制台登录指令重新配置 `SWR_USERNAME` 和 `SWR_PASSWORD`，并确认 `SWR_REGISTRY` 不带 `https://` 和组织路径后，流水线成功通过。

### 附加题 3：C-1 分布式 AI 训练专题

本附加题选择 C-1 分布式 AI 训练，使用 PyTorch DDP 在 Kubernetes 中进行 MNIST CNN 训练，并与单机训练时间进行对比。训练代码位于 `ai-training/`，其中 `train_single.py` 是单机基线，`train_ddp.py` 是分布式训练脚本，镜像构建文件为 `ai-training/Dockerfile`，Kubernetes Job 文件位于 `deploy/k8s/ai-training/`。

本实验没有追求复杂模型结构，而是使用一个小型 CNN：两层卷积、一个全连接隐藏层和一个输出层。这样设计的原因是课程集群节点资源有限，MNIST CNN 能在 CPU 环境下稳定跑完，也便于把实验重点放在分布式训练流程、Pod 协同、数据切分和梯度同步机制上。单机和分布式两种训练都保持相同 epoch、batch size、学习率和数据目录。当前记录的云上结果为：单机训练 `51.534s`，2 Worker DDP 训练 `43.475s`，加速比约为 `1.19`。

单机训练由 `mnist-single-job.yaml` 启动一个 Job。容器中运行 `python train_single.py --epochs 2 --batch-size 128 --data-dir /work/data --cpu`，脚本读取 MNIST 数据集后按普通 DataLoader 顺序训练模型，并在最后输出 `mode=single`、样本数、epoch 数、设备和训练时间。这个结果作为分布式训练的基线。由于本次使用 CPU，并且模型较小，单机训练时间本身不长，因此后续 DDP 的提升幅度不会像大模型或 GPU 多卡训练那样明显。

分布式训练使用 `mnist-ddp-job.yaml`。该 YAML 先创建一个 headless Service `mnist-ddp`，再创建一个 Indexed Job。Job 设置 `completions=2`、`parallelism=2`，表示同时运行两个 Worker Pod。每个 Pod 通过 Kubernetes 提供的 `JOB_COMPLETION_INDEX` 获取自己的序号，并传给 `torchrun` 的 `--node_rank`。两个 Pod 使用 `mnist-ddp-0.mnist-ddp.default.svc.cluster.local` 作为 master 地址，端口为 `29500`。这种设计让两个训练进程能在 Kubernetes DNS 中找到彼此，完成分布式进程组初始化。

`train_ddp.py` 启动后会调用 `torch.distributed.init_process_group` 初始化进程组。脚本根据是否有 GPU 选择 `nccl` 或 `gloo` 后端。本实验使用 CPU，因此实际使用 `gloo`。数据加载部分使用 `DistributedSampler`，它会根据 `world_size` 和当前 `rank` 将数据集划分为不同切片。这样每个 Worker 只处理自己的部分数据，避免两个 Worker 重复训练同一批样本。每个 epoch 开始前调用 `sampler.set_epoch(epoch)`，保证分布式采样在不同 epoch 中仍然可以正确打乱。

DDP 的核心机制是反向传播阶段的 AllReduce 梯度同步。每个 Worker 先根据自己的 mini-batch 做前向传播和反向传播，得到本地梯度。随后 DDP 会在 `loss.backward()` 过程中自动对模型参数梯度执行 AllReduce。可以把这个过程理解为：所有 Worker 把同一层参数的梯度相加，然后再除以 Worker 数量，得到平均梯度，并把这个平均梯度同步回每一个 Worker。这样每个 Worker 在执行 `optimizer.step()` 前看到的是同一份梯度，所以即使它们处理的是不同数据切片，模型参数仍能保持一致。

AllReduce 不是简单地把所有梯度先集中到某一个主节点再广播回去。成熟的通信库会使用环形、树形等方式把规约和分发过程结合起来，减少单点瓶颈。对于 DDP 来说，用户代码里不需要手动写每一层参数的通信逻辑，只要把模型包装成 `DistributedDataParallel(model)`，框架就会在反向传播时自动注册 hook 并触发梯度同步。这也是 PyTorch DDP 比手工参数服务器方式更适合课程实验的原因：代码结构清晰，能体现分布式训练的核心流程，同时不需要自己维护复杂的梯度通信细节。

本实验采用的是数据并行，不是模型并行。数据并行的特点是每个 Worker 都保存一份完整模型，只是输入数据不同；训练时通过同步梯度保证所有模型副本参数一致。模型并行则是把一个模型拆成多个部分，放到不同设备或节点上，例如把大模型的不同层拆到不同 GPU。MNIST CNN 很小，单个节点完全可以容纳完整模型，如果强行做模型并行，通信次数和中间激活传输反而会增加，实验重点也会偏离任务书要求。因此本实验选择数据并行更合理。

从结果看，2 Worker DDP 比单机略快，但加速比只有约 `1.19`。这个结果是合理的。MNIST CNN 的计算量较小，单个 batch 前向和反向传播时间很短，而 DDP 需要额外的 rendezvous、进程组初始化、DistributedSampler 切分、梯度 AllReduce 和 Pod 调度开销。这些开销会抵消一部分并行收益。当模型更大、单步计算量更高、epoch 更多、硬件使用 GPU 时，数据并行的收益通常会更明显。本实验的价值主要在于验证 DDP 能够在 CCE/Kubernetes 上跑通，并观察到小模型场景下通信开销对加速比的影响。

操作步骤摘要：

```bash
kubectl delete job mnist-single mnist-ddp --ignore-not-found
kubectl delete svc mnist-ddp --ignore-not-found

kubectl apply -f deploy/k8s/ai-training/mnist-single-job.yaml
kubectl wait --for=condition=complete job/mnist-single --timeout=30m
kubectl get pods -l job-name=mnist-single -o wide
kubectl logs job/mnist-single

kubectl apply -f deploy/k8s/ai-training/mnist-ddp-job.yaml
kubectl wait --for=condition=complete job/mnist-ddp --timeout=30m
kubectl get pods -l job-name=mnist-ddp -o wide
kubectl logs job/mnist-ddp
```

关键截图：

> 待补截图：`4.3-C-1-mnist-single-pod-completed.png`，展示单机 Job Completed。  
> 待补截图：`4.3-C-1-mnist-single-log-current.png`，展示单机 `train_time=51.534s` 或最终实际时间。  
> 待补截图：`4.3-C-1-mnist-ddp-pods-completed.png`，展示 2 个 DDP Pod Completed。  
> 待补截图：`4.3-C-1-mnist-ddp-log-current.png`，展示 DDP `workers=2` 和 `train_time=43.475s` 或最终实际时间。

问题与解决方案：  
训练镜像中预下载 MNIST 数据集，但脚本仍保留 `--allow-synthetic` 兜底。如果最终日志显示 `dataset=synthetic-mnist-shaped`，报告必须如实说明使用了 MNIST 形状的合成数据，不能写成真实 MNIST。本次报告正文按当前记录的 `dataset=mnist` 口径撰写，最终以重新补的日志截图为准。

## 总结与收获

这次课程设计让我对云计算平台从“会用容器”进一步推进到“能把应用放到真实 Kubernetes 环境里运行”。本地 Docker Compose 只解决了单机联调问题，而 CCE 部署还要考虑镜像仓库、私有镜像拉取、Service 暴露、ELB 绑定、ConfigMap/Secret 配置分离、PVC 持久化和 HPA 指标来源等问题。尤其是 HPA 和监控系统让我意识到，云上应用不是 Pod Running 就算完成，还需要持续观察资源使用、扩缩容行为和故障恢复能力。

实验中比较大的挑战来自环境差异和证据一致性。KubeConfig、SWR 登录 token、GitHub Secrets 都不能写入仓库，但部署和流水线又必须依赖它们；旧账号和新账号之间的 ELB IP、SWR 组织名、镜像 Tag 也很容易混用。监控系统中 kube-prometheus-stack 还遇到了 CRD 版本兼容问题，最后选择保留 Grafana、自建 Prometheus 的折中方案，这让我认识到真实云环境里经常需要在任务要求、平台限制和风险控制之间做取舍。MPI 和 DDP 部分则让我看到，分布式并不天然更快，通信、同步和调度开销会直接影响性能，只有结合问题规模和运行环境分析结果才有意义。

## 附录

### 代码与配置文件位置

本报告附录不逐字粘贴全部源码，完整修改后的文件以 GitHub 仓库为准：

```text
https://github.com/want-be-human/yjs-final
```

核心文件清单：

- `app/backend/app.py`
- `app/backend/requirements.txt`
- `app/backend/Dockerfile.backend`
- `app/frontend/Dockerfile.frontend`
- `app/frontend/nginx.conf`
- `app/frontend/static/index.html`
- `docker-compose.yml`
- `deploy/k8s/app/deployment.yaml`
- `deploy/k8s/app/frontend-deployment.yaml`
- `deploy/k8s/app/service.yaml`
- `deploy/k8s/app/redis-deployment.yaml`
- `deploy/k8s/app/redis-pvc.yaml`
- `deploy/k8s/app/configmap.yaml`
- `deploy/k8s/app/secret.yaml`
- `deploy/k8s/app/nginx-configmap.yaml`
- `deploy/k8s/app/backend-hpa.yaml`
- `deploy/k8s/mpi/mpijob.yaml`
- `deploy/k8s/mpi/integral-mpijob.yaml`
- `mpi/integral_serial.py`
- `mpi/integral_mpi.py`
- `mpi/integral_mpi_nonblocking.py`
- `mpi/bench_mpi.py`
- `mpi/plot_amdahl.py`
- `deploy/k8s/monitoring/monitoring-values.yaml`
- `deploy/k8s/monitoring/yjs-prometheus.yaml`
- `deploy/k8s/monitoring/grafana-datasource.yaml`
- `.github/workflows/deploy.yml`
- `ai-training/train_single.py`
- `ai-training/train_ddp.py`
- `ai-training/Dockerfile`
- `deploy/k8s/ai-training/mnist-single-job.yaml`
- `deploy/k8s/ai-training/mnist-ddp-job.yaml`

### 提交前检查

最终提交前需要确认：

- 报告中所有 IP 均为当前后端公网 IP `114.116.194.77`。
- 报告中所有 SWR 组织均为 `yjs-final`。
- C-1 训练时间和截图日志一致。
- GitHub Actions 截图显示 `build-and-deploy` 已 Passed。
- KubeConfig、SWR token、AK/SK 没有进入仓库或报告。
