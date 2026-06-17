# 成员 B 本地完成记录

## 已对照任务书完成的本地部分

### 任务1 应用容器化

- 前端页面在 `app/frontend/static/index.html`，已包含学号和姓名。
- 前端 Dockerfile 在 `app/frontend/Dockerfile.frontend`，按任务书 Nginx 静态页模板写。
- Nginx 反向代理配置在 `app/frontend/nginx.conf`，本地走 `backend:5000`。
- `docker-compose.yml` 已包含前端、后端和 Redis，本地运行需要在 WSL 里执行。
- 已在 WSL 中执行 `docker compose up --build -d`，三个容器均启动成功。
- 已通过 `curl http://localhost:8080/api/ping` 验证 Nginx 到 Flask 到 Redis 链路，返回 `status=ok`、`redis=ok`。
- 已将前端页面学生信息更新为 `2023112473 谢梦瑶`。
- 已保存本地前端接口截图和后端 `/api/ping` 日志截图到 `docs/screenshots/`。
- 已在华为云 SWR 华北-北京四创建组织 `yjs-final-2023112473`。
- 已使用临时登录指令登录 SWR，并推送前端、后端镜像。
- 已推送后端镜像：`swr.cn-north-4.myhuaweicloud.com/yjs-final-2023112473/yjs-backend:v1`。
- 已推送前端镜像：`swr.cn-north-4.myhuaweicloud.com/yjs-final-2023112473/yjs-frontend:v1`。
- 普通 `docker push` 后端镜像时遇到 SWR manifest 解析错误，已改用 `docker buildx build --platform linux/amd64 --provenance=false --push` 解决。

待补：
- SWR 前端/后端镜像列表截图，必须包含镜像名和 Tag。

### 任务2 CCE 集群搭建

- 已在华为云华北-北京四创建 CCE Standard 集群 `yjs-final-cluster`。
- Kubernetes 版本为 `v1.35.3-r0-35.0.8`，满足任务书要求的 `>= 1.27`。
- 已创建 2 个 Worker 节点，节点规格为 `c9.large.2`（2 vCPU / 4 GiB），操作系统为 Ubuntu 22.04，容器运行时为 containerd。
- HPA 阶段因资源不足新增 1 个 2 vCPU / 8 GiB Worker 节点，用于支撑 Metrics Server、压测和后续 MPI/监控实验。
- 已创建 VPC `vpc-yjs-final`（`192.168.0.0/16`）和子网 `subnet-yjs-final`（`192.168.0.0/24`）。
- 已为 CCE API Server 临时绑定 1 Mbit/s 按需 EIP，下载公网访问版 kubeconfig。
- 已在 WSL 中配置 `~/.kube/config`，`kubectl get nodes -o wide` 能看到两个节点均为 `Ready`。
- 已执行 `kubectl get pods -A`，确认 `coredns`、`everest-csi`、`icagent`、`node-local-dns` 等系统 Pod 为 `Running`。

待补：
- 控制台节点 Ready 截图和 WSL 终端 `kubectl get nodes -o wide` 截图归档。
- 实验结束后释放 CCE 集群、节点、EIP、ELB 和云硬盘，避免持续计费。

### 任务3 应用部署

- `deploy/k8s/app/service.yaml` 已写后端 `LoadBalancer` Service，并加 `kubernetes.io/elb.class: union`。
- 同文件已写 Redis `ClusterIP` Service。
- 为了能完整 apply，本地补了后端、Redis、ConfigMap、Secret、PVC 等 YAML，其中任务书模板文件名已对齐为 `deployment.yaml`、`configmap.yaml`、`secret.yaml`。
- 已将后端和前端 Deployment 镜像地址替换为 `yjs-final-2023112473` 下的真实 SWR 镜像。
- 已在 CCE 上部署 backend、frontend、Redis、PVC、ConfigMap、Secret 和 Service。
- 因默认 Service 未自动创建 ELB，已手动创建共享型 ELB `elb-yjs-backend`，并在 `backend-svc` 注解中绑定负载均衡器 ID。
- `backend-svc` 已获得公网 IP `1.92.115.240`，通过 `curl http://1.92.115.240/api/ping` 验证返回成功。
- 部署过程中因小规格节点资源紧张，将后端和 Redis 的 requests/limits 调小，并将后端滚动更新策略改为 `maxSurge=0`、`maxUnavailable=1`，避免滚动更新时额外 Pod 卡住。

待补：
- 归档 CCE 上 `kubectl get deploy`、`kubectl get pods -o wide`、`kubectl get svc` 和 `/api/ping` 成功访问截图。

### 任务4 Redis 持久化

- 已创建 Redis PVC `redis-data-pvc`，状态为 `Bound`，容量为 `10Gi`，StorageClass 为 `csi-disk`。
- 已完成持久化验证：写入 `testkey`，删除 Redis Pod，等待新 Pod 自动重建后再次读取 `testkey` 成功。

待补：
- 归档 PVC Bound、写入 key、删除 Pod、新 Pod 读取 key 成功的截图。

### 任务5 ConfigMap Volume

- `deploy/k8s/app/nginx-configmap.yaml` 已把完整 Nginx 配置放入 ConfigMap。
- `deploy/k8s/app/frontend-deployment.yaml` 已把 ConfigMap 挂载到 `/etc/nginx/conf.d`。
- 没有使用 `subPath`，因为 `subPath` 挂单文件时 ConfigMap 更新不会自动同步到容器内文件，不符合任务书要求。

待补：
- CCE 上 apply 后 exec 进前端 Pod：`cat /etc/nginx/conf.d/default.conf` 截图。
- 把 ConfigMap 里的后端端口临时改成错误值再 apply，验证 Pod 内文件变更的截图。

### 任务6 HPA

- `deploy/k8s/app/backend-hpa.yaml` 已按任务书写：`minReplicas=1`，`maxReplicas=4`，CPU 目标 60%。
- 已安装 Kubernetes Metrics Server 插件。
- 因 Metrics Server 初始 Pending 且事件显示 `Insufficient memory`，按任务书建议新增 1 个 2 vCPU / 8 GiB 节点后插件 Running。
- `kubectl top nodes` 已能看到节点 CPU 和内存指标。
- 已创建 `backend-hpa`，指标显示正常，例如 `cpu: 2%/60%`。
- 使用 `busybox` 压测 Pod 持续访问 `backend-svc/api/ping`，HPA 触发扩容，CPU 曾升至约 `213%/60%`，后端副本扩容到 4。
- 停止压测并删除 load-generator Pod 后，HPA 完成缩容验证。

待补：
- 归档 `kubectl top nodes`、HPA 创建、扩容到 4、停止压测后缩容的截图。

### B-1 并行算法实现

- `mpi/integral_serial.py` 是串行梯形法。
- `mpi/integral_mpi.py` 是阻塞 MPI 版，使用 `scatter` 分发区间、`reduce` 汇总积分。
- `mpi/pi_mpi.py` 是任务书 B-0 的 MPIJob 入门验证示例。
- `mpi/Dockerfile` 可构建包含本仓库 MPI 脚本的 `yjs-mpi:v2` 镜像，避免 MPIJob 引用的 `/opt/mpi/*.py` 在基础镜像里不存在。
- `docs/report-notes/mpi-communication.md` 已放通信示意素材。
- 已在 WSL 中安装 MPI/`mpi4py` 运行串行版和 4 进程 MPI 版，完成结果一致性验证。
- 已保存截图：`docs/screenshots/mpi-b1-serial-vs-parallel-consistency.png`。

云上补充：
- 已在 CCE 上部署 MPI Operator，截图为 `docs/screenshots/cce-mpi-operator-running.png`。
- 已构建并推送 `swr.cn-north-4.myhuaweicloud.com/yjs-final-2023112473/yjs-mpi:v2`，镜像包含本仓库 MPI 脚本、`mpi4py`、OpenMPI 和 `openssh-server`。
- 已将 MPIJob `apiVersion` 修正为 `kubeflow.org/v2beta1`，并在 `mpirun` 中加入 `--allow-run-as-root` 和 `--oversubscribe`。
- 已在 CCE 上运行 `mpi-pi` MPIJob，Launcher Job 完成状态为 `Complete 1/1`。
- 已保存截图：`docs/screenshots/cce-mpijob-pods-completed.png`、`docs/screenshots/cce-mpijob-job-complete.png`、`docs/screenshots/cce-mpijob-pi-log.png`。

建议补充：
- 可再补一张 SWR 控制台 `yjs-mpi:v2` 标签截图，命名为 `docs/screenshots/cce-swr-mpi-v2.png`。

### B-2 性能测试与 Amdahl 分析

- `mpi/bench_mpi.py` 可按 1、2、4 进程各跑 3 次并生成 CSV。
- `mpi/plot_amdahl.py` 可根据 CSV 画实测加速比和 Amdahl 理论加速比双折线图。
- 已在 WSL 中按 `steps=10000000`、每组重复 3 次完成真实性能测试。
- 已生成 `docs/report-notes/mpi-benchmark.csv`、`docs/report-notes/mpi-benchmark.log` 和 `docs/report-notes/mpi-amdahl.png`。
- 当前实测结果：1 进程平均 `0.767674s`，2 进程平均 `0.379951s`，4 进程平均 `0.212694s`，4 进程加速比约 `3.6093`。

待补：
- 报告里结合真实数据补充加速比与 Amdahl 理论差距分析。

### B-3 非阻塞通信优化

- `mpi/integral_mpi_nonblocking.py` 已用 `isend/irecv` 改写任务分发和结果回传。
- `mpi/compare_blocking_nonblocking.py` 可对比 4 进程下阻塞版和非阻塞版时间。
- 已在 WSL 中完成 4 进程阻塞版与非阻塞版对比，并保存截图：`docs/screenshots/mpi-b3-blocking-vs-nonblocking.png`。

待补：
- 根据真实时间写适用条件分析。

### C-1 分布式 AI 训练

- `ai-training/train_single.py` 是单机 MNIST CNN 训练脚本。
- `ai-training/train_ddp.py` 是 PyTorch DDP 版本。
- `ai-training/Dockerfile` 已准备训练镜像构建文件。
- `deploy/k8s/ai-training/mnist-single-job.yaml` 是单机基线 Job。
- `deploy/k8s/ai-training/mnist-ddp-job.yaml` 是 2 Worker Pod 的 DDP Indexed Job。
- `docs/report-notes/c1-distributed-ai-training.md` 已写专题主体，并补入真实训练时间和分析。
- 已构建并推送 `swr.cn-north-4.myhuaweicloud.com/yjs-final-2023112473/mnist-ddp:v3`。
- 镜像构建阶段已预下载真实 MNIST 数据到 `/work/data`，避免 CCE Pod 运行时访问 MNIST 官方源超时。
- 单机 Job 训练结果：`mode=single dataset=mnist samples=60000 epochs=2 device=cpu train_time=35.509s`。
- 2 Worker DDP Job 训练结果：`mode=ddp dataset=mnist samples=60000 workers=2 epochs=2 device=cpu train_time=39.128s`。
- 加速比为 `0.9074`，DDP 略慢，原因是小模型小数据集下通信和调度开销超过并行计算收益。

建议补充：
- 确认 `docs/screenshots/` 中已保存 `c1-mnist-single-pod-completed.png`、`c1-mnist-single-log.png`、`c1-mnist-ddp-pods-completed.png`、`c1-mnist-ddp-log.png`。

### 附加题 1 监控系统

- 已确认离线包提供 `monitoring-all.tar`、`kube-prometheus-stack-83.7.0.tgz` 和 `monitoring-values.yaml`。
- 已在 `deploy/k8s/monitoring/` 放置部署说明和 values 模板。
- 已整理 `docs/report-notes/monitoring-report-notes.md`，包含 Prometheus Pull 原理、截图清单和指标说明。

待补：
- 把监控镜像加载、重新 tag 到个人 SWR 并推送。
- 替换 `<region>` 和 `<your-organization>`。
- CCE 上安装 kube-prometheus-stack。
- 保存 Grafana 节点 CPU 折线图和 Pod 内存柱状图截图。

### 附加题 2 CI/CD 流水线

- 已新增 `.github/workflows/deploy.yml`。
- Workflow 会构建前端/后端镜像、推送 SWR，并更新 `backend`、`frontend` Deployment 镜像 tag。
- 已整理 `docs/report-notes/cicd-report-notes.md`，包含 Secrets 清单和报告说明点。

待补：
- 在 GitHub 仓库配置 `SWR_REGISTRY`、`SWR_ORG`、`SWR_USERNAME`、`SWR_PASSWORD`、`KUBE_CONFIG`。
- 首次运行前确认 CCE 上已有 `backend` 和 `frontend` Deployment。
- 保存 GitHub Actions Passed、SWR 新 tag、Deployment 镜像更新截图。
