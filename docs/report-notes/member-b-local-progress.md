# 成员 B 完成记录

## 当前基准

- 运行环境以 WSL 为准，Windows 只作为编辑环境。
- 当前华为云区域为 `cn-north-4`，SWR 组织为 `yjs-final`。
- CCE 集群为 `yjs-final-cluster`，kubeconfig 已能在本地访问集群。
- 新账号环境已经重新部署并完成主要云上验证，截图仍需按报告要求补齐。

## 任务 1 应用容器化

- 前端静态页面在 `app/frontend/static/index.html`。
- 后端 Flask 应用在 `app/backend/app.py`，`/api/ping` 会检查 Redis。
- 前端、后端 Dockerfile 分别为 `app/frontend/Dockerfile.frontend` 和 `app/backend/Dockerfile.backend`。
- `docker-compose.yml` 已包含 frontend、backend、redis，本地可用于联调。
- K8s 镜像地址已切到 `swr.cn-north-4.myhuaweicloud.com/yjs-final/`。

已验证：

- 前端、后端镜像已推送到新账号 SWR。
- 后端公网 `/api/ping` 已返回 `status=ok`，Redis 状态为 `ok`。

## 任务 2 CCE 集群搭建

- 已创建 CCE Standard 集群 `yjs-final-cluster`。
- 已验证 kubeconfig 可访问集群，节点状态为 Ready。
- 当前节点为 3 个 Worker，满足应用、HPA、MPI、监控的基本运行需要。

待补证据：

- CCE 控制台集群概览截图。
- `kubectl get nodes -o wide` 截图。
- 实验结束后释放 CCE、节点、ELB、EIP、云硬盘等按需资源。

## 任务 3 应用部署

- `deploy/k8s/app/deployment.yaml` 为后端 Deployment。
- `deploy/k8s/app/frontend-deployment.yaml` 为前端 Deployment。
- `deploy/k8s/app/service.yaml` 包含后端 LoadBalancer Service 和 Redis ClusterIP Service。
- `deploy/k8s/app/configmap.yaml`、`secret.yaml`、`redis-deployment.yaml`、`redis-pvc.yaml` 已准备。
- 已绑定新账号 ELB，公网地址为 `114.116.194.77`。

已验证：

- `backend`、`frontend`、`redis` Pod 均为 Running。
- `backend-svc` 已绑定公网 ELB，`/api/ping` 访问成功。

## 任务 4 Redis 持久化

- Redis 使用 `redis-data-pvc`，StorageClass 为 `csi-disk`。
- Redis Deployment 使用 `Recreate` 策略，避免同一块云硬盘被新旧 Pod 同时挂载。

待补证据：

- PVC Bound 截图。
- 写入 key、删除 Redis Pod、重建后读取 key 成功的截图。
已完成云上验证：写入 key、删除 Redis Pod、重建后读取 key 成功。

## 任务 5 ConfigMap Volume

- `deploy/k8s/app/nginx-configmap.yaml` 保存 Nginx 配置。
- 前端 Deployment 将 ConfigMap 挂载到 `/etc/nginx/conf.d`。
- 没有使用 `subPath`，方便 ConfigMap 更新后同步到容器内文件。

待补证据：

- `kubectl exec` 查看 `/etc/nginx/conf.d/default.conf` 截图。
- 修改 ConfigMap 后容器内文件更新截图。
已完成云上验证：前端容器内 `/etc/nginx/conf.d/default.conf` 能看到 ConfigMap 挂载内容，更新后文件同步生效。

## 任务 6 HPA

- `deploy/k8s/app/backend-hpa.yaml` 已配置 `minReplicas=1`、`maxReplicas=4`、CPU 目标 60%。
- 需要集群 metrics 能正常返回，才能完成扩缩容验证。
- 新账号中 metrics-server 已部署，HPA 已完成扩容和缩容验证。

待补证据：

- `kubectl top nodes` 截图。
- HPA 创建、压测扩容、停止压测后缩容截图。
已完成云上验证：压测时后端扩到 4 个副本，停止压测后缩回 1 个副本。

## B-0 MPIJob 示例

- MPI Operator 使用离线包里的 `mpi-operator.yaml`。
- `deploy/k8s/mpi/mpijob.yaml` 使用 `kubeflow.org/v2beta1`。
- MPI 镜像优先使用老师提供的 `mpi4py:latest`，重新 tag 到个人 SWR。
- 本仓库 Python 脚本通过 `mpi-scripts` ConfigMap 挂载到 MPIJob Pod。

待补证据：

- MPI Operator Running 截图。
- MPIJob Pod 完成截图。
- launcher 日志中 π 计算结果截图。
已完成云上验证：`mpi-pi` 和 `integral-mpi` 均成功，`integral-mpi` 输出 `pi=3.141592653590`。

## B-1 到 B-3 并行算法

- `mpi/integral_serial.py`：串行梯形积分。
- `mpi/integral_mpi.py`：阻塞 MPI 版本。
- `mpi/integral_mpi_nonblocking.py`：非阻塞 MPI 版本。
- `mpi/bench_mpi.py`：1、2、4 进程性能测试。
- `mpi/plot_amdahl.py`：生成实测加速比和 Amdahl 理论曲线。
- `mpi/compare_blocking_nonblocking.py`：对比阻塞和非阻塞版本。
- 本地已有历史测试数据和图表，换新云环境不影响这部分本地结论。

待补证据：

- 把本地终端运行截图和 `mpi-amdahl.png` 放入正式报告。
- 报告中说明小规模任务下非阻塞版本不一定更快，原因是通信无法和计算充分重叠。

## C-1 分布式 AI 训练

- `ai-training/train_single.py` 为单机训练脚本。
- `ai-training/train_ddp.py` 为 PyTorch DDP 训练脚本。
- `deploy/k8s/ai-training/mnist-single-job.yaml` 为单机 Job。
- `deploy/k8s/ai-training/mnist-ddp-job.yaml` 为 2 Worker Indexed Job。
- 当前镜像地址为 `swr.cn-north-4.myhuaweicloud.com/yjs-final/mnist-ddp:v3`。
- 新账号云上结果：单机 `51.534s`，2 Worker DDP `43.475s`，加速比约 `1.19`。

已完成云上验证：单机 Job 和 2 Worker DDP Job 均 Completed，日志已输出训练时间。

## 附加题 1 监控系统

- 离线包包含 `monitoring-all.tar`、`kube-prometheus-stack-83.7.0.tgz` 和 values。
- `deploy/k8s/monitoring/monitoring-values.yaml` 已切到 `cn-north-4/yjs-final`。
- CCE 自带旧版 Prometheus Operator CRD 与新版 Chart 字段不兼容，当前采用 Chart 部署 Grafana、自建 `yjs-prometheus` 采集指标。
- Grafana datasource 已连到 `yjs-prometheus`，Prometheus 已能查询节点 CPU 和 Pod 内存指标。
- 报告素材在 `docs/report-notes/monitoring-report-notes.md`。

待补截图：

- Helm 安装成功截图。
- Grafana 节点 CPU 折线图。
- Grafana Pod 内存柱状图。
- 报告中说明 Prometheus Pull 原理和至少 3 个指标含义。

## 附加题 2 CI/CD 流水线

- workflow 文件为 `.github/workflows/deploy.yml`。
- workflow 会构建前端/后端镜像，推送 SWR，然后更新 `backend`、`frontend` Deployment。
- 报告素材在 `docs/report-notes/cicd-report-notes.md`。

待补证据：

- GitHub 中需要 5 个独立 Repository secrets：`SWR_REGISTRY`、`SWR_ORG`、`SWR_USERNAME`、`SWR_PASSWORD`、`KUBE_CONFIG`。只配置 `YJS_SECRET` 时，现有 workflow 不会读取。
- GitHub Actions Passed 截图。
- SWR 新 tag 截图。
- Deployment 镜像 tag 更新截图。
