# 开发日志

## 2026-06-12

- 阅读 `课程设计任务书-final.pdf`，整理课程设计完成路线。
- 新增 `course-project-steps.md`，记录任务拆分、截图清单、代码缺口、可协助部分和需要本人完成的部分。
- 检查 `linux-amd64`，确认里面是 Linux amd64 平台的 Helm 客户端，用于安装 Kubernetes Chart，比如 Spark Operator 或 kube-prometheus-stack。
- 确认实验选择：第二部分选 MPI 方向，算法题选数值积分；附加题选前沿专题里的分布式 AI 训练；本地环境准备用 WSL。
- 新增 `team-work-division.md`，按任务书的任务 1-6、B-0 到 B-3、C-1 附加题拆分两人工作，目标是 50% / 50%。
- 新增 `member-a-guide.md` 和 `member-b-guide.md`，分别给两名成员整理任务来源、评分注意事项、实验记录要求和联调节点。
- 将成员 A 发来的 `cloud-course-task1` 拆到仓库结构：`app/backend`、`app/frontend`、`docker-compose.yml`，并补出 `deploy/k8s`、`mpi`、`ai-training`、`docs/screenshots` 等后续位置。
- 更新成员 A/B 指导书，补充 WSL 运行前提和需要创建文件的位置。

遗留：

- 还没有生成实验代码，需要先确认学号、姓名、班级。
- 华为云 SWR、CCE、KubeConfig、教师离线包和镜像地址需要后续补齐。

## 2026-06-13

- 按成员 B 指导书和任务书 PDF 核对了任务 1、3、5、6、B-1、B-2、B-3、C-1 的要求。
- 明确当前边界：Windows 里写代码，运行和本地部署按 WSL 路径 `/mnt/d/vsCode/python/yjs` 执行；新补文本和代码保持 UTF-8 / LF。
- 补齐 `deploy/k8s/app/` 下的 Service、后端 HPA、Nginx ConfigMap、前端 Deployment、后端/Redis 基础部署、Redis PVC、ConfigMap 和 Secret。
- ConfigMap Volume 没用 `subPath`，因为单文件 `subPath` 挂载不会跟随 ConfigMap 更新，和任务书“修改后 exec 验证文件已更新”的要求冲突。
- 补齐 `mpi/` 下的串行梯形法、阻塞 MPI、非阻塞 MPI、性能测试脚本、Amdahl 画图脚本和 4 进程对比脚本。
- 补了 `mpi/pi_mpi.py`、`mpi/Dockerfile` 和 `deploy/k8s/mpi/mpijob.yaml`，用于 B-0 示例作业和把本仓库 MPI 脚本带进镜像。
- Redis Deployment 改为从 `redis-secret` 注入密码，不再把密码直接写在 Redis 启动参数里。
- 补齐 `ai-training/` 下的单机 MNIST CNN、PyTorch DDP 训练脚本、训练镜像 Dockerfile，以及 `deploy/k8s/ai-training/` 下的单机 Job 和 2 Worker DDP Job。
- 新增 `docs/report-notes/member-b-local-progress.md`，逐项记录成员 B 本地已完成和待云上补证据的部分。
- 新增 `docs/report-notes/mpi-communication.md` 和 `docs/report-notes/c1-distributed-ai-training.md`，作为报告素材。
- WSL 验证已做：Python 脚本语法检查通过，串行积分可运行，`docker compose config` 可解析，K8s YAML 可用 PyYAML 解析。
- WSL 中 `docker compose up --build -d` 已成功，`curl http://localhost:8080/api/ping` 返回 `status=ok`、`redis=ok`，后端日志能看到 `/api/ping` 请求。
- 按任务书脚手架模板统一了关键文件名：`Dockerfile.backend`、`Dockerfile.frontend`、`docker-compose.yml`、`deployment.yaml`、`configmap.yaml`、`secret.yaml`、`mpijob.yaml`。

遗留：

- WSL 里目前没有 `mpi4py`，MPI 结果一致、性能测试、非阻塞对比暂时不能真实运行。
- 云上相关内容还缺 SWR 组织名、镜像推送、CCE KubeConfig、ELB IP、HPA 扩缩容截图和 AI 训练 Pod 日志。

## 2026-06-14

- 检查 `离线包/README.md` 和离线包目录，确认里面已有 MPI 和监控系统继续推进所需资源：`mpi4py-latest.tar`、`mpi-operator.yaml`、`monitoring-all.tar`、`kube-prometheus-stack-83.7.0.tgz` 和 `monitoring-values.yaml`。
- 确认离线包不包含 CI/CD 所需的 GitHub Secrets、SWR 登录信息、CCE KubeConfig，也没有 C-1 PyTorch DDP 训练镜像。
- 将附加题 1 监控系统和附加题 2 CI/CD 流水线补进成员 B 指导书；成员 A 指导书补充云资源、SWR 和 KubeConfig 配合项。
- 更新 `team-work-division.md`，把监控系统、CI/CD 流水线和 C-1 都纳入附加题分工。
- 新增 `deploy/k8s/monitoring/`，放监控部署说明和 `monitoring-values.template.yaml`，保留 `<region>`、`<your-organization>` 占位。
- 新增 `.github/workflows/deploy.yml`，用于构建前后端镜像、推送 SWR、更新 CCE Deployment；所有敏感值均从 GitHub Secrets 读取。
- 新增 `docs/report-notes/offline-resources.md`、`monitoring-report-notes.md`、`cicd-report-notes.md`，整理离线资源、监控报告素材和 CI/CD 报告素材。

遗留：

- 监控系统部署还需要真实 Region、SWR 组织名、SWR 登录信息、CCE KubeConfig 和 Grafana 截图。
- CI/CD 还需要在 GitHub 仓库配置 `SWR_REGISTRY`、`SWR_ORG`、`SWR_USERNAME`、`SWR_PASSWORD`、`KUBE_CONFIG`。
- C-1 分布式 AI 训练仍需联网构建 PyTorch 训练镜像并推送 SWR，或由用户提供可用训练镜像。

## 2026-06-14 本地补充记录

- 更新前端页面学生信息为 `2023112473 谢梦瑶`。
- 补齐本地任务 1 证据：已保存前端页面访问接口截图和后端收到 `/api/ping` 日志截图到 `docs/screenshots/`。
- 在 WSL 虚拟环境中安装并验证 MPI/`mpi4py`，完成串行梯形法和 4 进程 MPI 并行版结果一致性验证，截图为 `docs/screenshots/mpi-b1-serial-vs-parallel-consistency.png`。
- 完成本地 MPI 性能测试：`steps=10000000`，1/2/4 进程各运行 3 次，生成 `docs/report-notes/mpi-benchmark.csv`、`mpi-benchmark.log` 和 `mpi-amdahl.png`。
- 当前本地 MPI 测试结果：1 进程平均 `0.767674s`，2 进程平均 `0.379951s`，4 进程平均 `0.212694s`，4 进程实测加速比约 `3.6093`，反推可并行比例约 `0.9639`。
- 完成 4 进程阻塞 MPI 与非阻塞 MPI 对比截图，保存为 `docs/screenshots/mpi-b3-blocking-vs-nonblocking.png`。

遗留：

- 云上 MPIJob B-0 仍需替换真实 SWR 镜像地址，在 CCE 上运行并保存 Launcher/Worker Pod 和 π 输出日志截图。
- 当前 `.gitignore` 会忽略 `docs/screenshots/*` 和 `docs/report-notes/` 下的非 Markdown 生成文件；最终提交截图和图表时需要调整忽略规则或使用强制添加。

## 2026-06-15

- 在华为云华北-北京四区域创建 CCE Standard 集群 `yjs-final-cluster`，Kubernetes 版本为 `v1.35`，计费模式为按需计费。
- 为集群创建 VPC `vpc-yjs-final`，网段为 `192.168.0.0/16`；创建子网 `subnet-yjs-final`，网段为 `192.168.0.0/24`。
- 集群网络使用 VPC 网络模型，容器网段为 `10.0.0.0/16`，Service CIDR 为 `10.247.0.0/16`，服务转发模式为 `nftables`。
- 创建 2 个 Worker 节点，节点规格为 `c9.large.2`（2 vCPU / 4 GiB），操作系统为 Ubuntu 22.04，容器运行时为 containerd，cgroup 版本为 v2。
- 在 CCE 中保留基础插件：Yangtse CNI、Everest、CoreDNS 和 NodeLocal DNSCache；未启用云原生监控、日志采集和节点故障检测等额外可观测性插件。
- 为 CCE API Server 临时购买并绑定按需弹性公网 IP，带宽 1 Mbit/s，用于从本地 WSL 通过 `kubectl` 访问集群。
- 下载公网访问版 kubeconfig，并在 WSL 中配置到 `~/.kube/config`；执行 `kubectl get nodes -o wide` 成功看到两个节点均为 `Ready`。
- 执行 `kubectl get pods -A` 验证系统组件运行状态，`coredns`、`everest-csi`、`icagent` 和 `node-local-dns` 等 Pod 均为 `Running`。
- 在 SWR 中创建组织 `yjs-final-2023112473`，选择 6 小时临时登录指令完成本地 Docker 登录。
- 使用 `docker buildx build --platform linux/amd64 --provenance=false --push` 重新构建并推送前后端镜像到 SWR，解决普通 `docker push` 时 SWR 无法解析镜像 manifest 的问题。
- 已推送镜像：
  - `swr.cn-north-4.myhuaweicloud.com/yjs-final-2023112473/yjs-backend:v1`
  - `swr.cn-north-4.myhuaweicloud.com/yjs-final-2023112473/yjs-frontend:v1`
- 将 `deploy/k8s/app/deployment.yaml` 和 `deploy/k8s/app/frontend-deployment.yaml` 中的 `<YOUR_ORG>` 替换为真实 SWR 组织名 `yjs-final-2023112473`。
- 在 CCE 上部署 `Secret`、`ConfigMap`、Redis PVC、Redis Deployment、后端 Deployment、前端 Deployment 和 Service。
- Redis PVC 已成功绑定，`redis-data-pvc` 状态为 `Bound`，容量为 `10Gi`，StorageClass 为 `csi-disk`。
- 初次部署时 Redis 和后端 Pod 因节点资源紧张出现 `Insufficient memory` 和滚动更新卡住问题；已将 Redis 资源调整为 `requests: 50m/64Mi`、`limits: 200m/256Mi`，将后端资源调整为 `requests: 50m/64Mi`、`limits: 300m/256Mi`。
- 为后端 Deployment 增加滚动更新策略 `maxSurge: 0`、`maxUnavailable: 1`，避免小规格节点上滚动更新时临时创建额外 Pod 导致资源不足。
- 手动创建共享型 ELB `elb-yjs-backend`，并将负载均衡器 ID `b17243e5-008d-4407-bb98-8b37d4a8d2d9` 写入 `backend-svc` 注解 `kubernetes.io/elb.id`。
- `backend-svc` 已获得公网 IP `1.92.115.240`，并通过 `curl http://1.92.115.240/api/ping` 验证云上后端接口和 Redis 链路正常。
- 完成 Redis 持久化验证：写入 `testkey`，删除 Redis Pod 后由 Deployment 自动重建，新 Pod 中仍能读取原 key，证明 PVC 挂载生效。
- 安装 Kubernetes Metrics Server 插件用于 HPA；因 2 个 2C4G 节点资源不足导致 metrics-server Pending，按任务书建议新增 1 个 2C8G Worker 节点后插件成功 Running。
- `kubectl top nodes` 已可正常返回节点 CPU/内存指标。
- 创建 `backend-hpa`，配置 `minReplicas=1`、`maxReplicas=4`、CPU 目标利用率 `60%`。
- 使用 `busybox` 压测 Pod 持续访问 `backend-svc/api/ping`，HPA 观测到 CPU 使用率升至约 `213%/60%`，后端副本自动扩容到 4；停止压测后 CPU 降低并完成缩容验证。

遗留：

- ConfigMap Volume 挂载验证截图、MPIJob 示例运行截图以及 SWR/CCE/Service/PVC/HPA 等截图已在 2026-06-16 继续补齐并归档到 `docs/screenshots/`。
- 还需在实验完成后及时释放 CCE 集群、节点、EIP、ELB 和相关云硬盘，避免持续计费。

## 2026-06-16

- 补齐 Amdahl 图归档：将 `docs/report-notes/mpi-amdahl.png` 复制到 `docs/screenshots/mpi-b2-amdahl-speedup.png`，用于报告截图引用。
- 补齐 SWR 截图：已保存 `cce-swr-repositories.png`、`cce-swr-backend-v1.png`、`cce-swr-frontend-v1.png`，覆盖前后端镜像仓库和 `v1` Tag。
- 补齐最新 3 Worker 节点截图：`docs/screenshots/cce-kubectl-get-nodes-3workers.png`，节点 `192.168.0.136`、`192.168.0.140`、`192.168.0.28` 均为 `Ready`，Kubernetes 版本为 `v1.35.3-r0-35.0.8`。
- 完成 ConfigMap Volume 验证截图归档：`cce-configmap-nginx-mounted.png` 和 `cce-configmap-nginx-updated.png` 已保存，证明前端 Pod 内 `/etc/nginx/conf.d/default.conf` 可通过 ConfigMap 挂载并随更新生效。
- 完成 B-0 云上 MPIJob 实验：
  - MPI Operator 已通过 `离线包/mpi/mpi-operator.yaml` 部署，截图为 `docs/screenshots/cce-mpi-operator-running.png`。
  - 将 MPIJob `apiVersion` 从 `kubeflow.org/v1` 修正为离线包 CRD 支持的 `kubeflow.org/v2beta1`。
  - 构建并推送自定义 MPI 镜像 `swr.cn-north-4.myhuaweicloud.com/yjs-final-2023112473/yjs-mpi:v2`。
  - MPI 镜像构建中解决了若干问题：Docker Hub/Debian 源下载慢，改用华为云 Debian/PyPI 源；SWR 普通 push manifest 不兼容，改用 `docker buildx build --platform linux/amd64 --provenance=false --push`；Worker 缺少 `/usr/sbin/sshd`，在镜像中加入 `openssh-server`；OpenMPI root 运行限制，给 `mpirun` 增加 `--allow-run-as-root`；slot 不足，增加 `--oversubscribe`。
  - 将 MPIJob 清理策略改为 `cleanPodPolicy: None`，方便保留 Pod 现场和日志截图。
  - 已保存 MPIJob 证据截图：`cce-mpijob-pods-completed.png`、`cce-mpijob-job-complete.png`、`cce-mpijob-pi-log.png`。
- 当前主线必做实验已经基本闭环：本地联调、SWR、CCE 应用部署、公网访问、Redis PVC、ConfigMap Volume、Metrics Server/HPA、本地 MPI B-1/B-2/B-3、云上 MPIJob B-0 均已有截图证据。
- 继续完成附加题 C-1 分布式 AI 训练：
  - 构建并推送训练镜像 `swr.cn-north-4.myhuaweicloud.com/yjs-final-2023112473/mnist-ddp:v3`。
  - 由于 CCE Pod 运行时访问 MNIST 官方数据源超时，改为在镜像构建阶段通过 `ai-training/download_mnist.py` 将真实 MNIST 数据预下载到 `/work/data`。
  - 单机 Job `mnist-single` 成功运行 2 个 epoch，日志结果为 `mode=single dataset=mnist samples=60000 epochs=2 device=cpu train_time=35.509s`。
  - DDP Job `mnist-ddp` 使用 2 个 Indexed Worker Pod 运行，rank 0 日志结果为 `mode=ddp dataset=mnist samples=60000 workers=2 epochs=2 device=cpu train_time=39.128s`。
  - 加速比为 `35.509 / 39.128 = 0.9074`。本实验中 DDP 略慢，原因是 MNIST CNN 模型小、CPU 计算量有限，AllReduce 同步和 Pod 调度/网络开销超过并行收益。
  - DDP 初次运行时第二个 Pod 因 `Insufficient memory`、`Insufficient cpu` Pending，已将训练 Job requests 调整为 `300m CPU / 768Mi`、limits 调整为 `1 CPU / 2Gi`，不改变训练逻辑，仅降低调度门槛。

遗留：

- 建议补一张 `yjs-mpi:v2` 的 SWR 控制台截图，命名为 `docs/screenshots/cce-swr-mpi-v2.png`，用于证明云上 MPIJob 镜像也来自 SWR。
- 附加题中 C-1 分布式 AI 训练已跑通；Prometheus/Grafana 监控和 GitHub Actions CI/CD 仍未实际部署，可根据时间和资源决定是否继续。
- 实验完成后仍需及时释放 CCE 节点、ELB、EIP、PVC 云硬盘等按需资源，避免继续计费。
