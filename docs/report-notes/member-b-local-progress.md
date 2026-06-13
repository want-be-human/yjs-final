# 成员 B 本地完成记录

## 已对照任务书完成的本地部分

### 任务1 应用容器化

- 前端页面在 `app/frontend/static/index.html`，已包含学号和姓名。
- 前端 Dockerfile 在 `app/frontend/Dockerfile`，按任务书 Nginx 静态页模板写。
- Nginx 反向代理配置在 `app/frontend/nginx.conf`，本地走 `backend:5000`。
- `compose.yaml` 已包含前端、后端和 Redis，本地运行需要在 WSL 里执行。
- 已在 WSL 中执行 `docker compose up --build -d`，三个容器均启动成功。
- 已通过 `curl http://localhost:8080/api/ping` 验证 Nginx 到 Flask 到 Redis 链路，返回 `status=ok`、`redis=ok`。

待补：
- 前端页面点击接口后的截图。
- 后端日志收到 `/api/ping` 的截图。
- SWR 前端镜像列表截图，必须包含镜像名和 Tag。

### 任务3 应用部署

- `deploy/k8s/app/service.yaml` 已写后端 `LoadBalancer` Service，并加 `kubernetes.io/elb.class: union`。
- 同文件已写 Redis `ClusterIP` Service。
- 为了能完整 apply，本地补了后端、Redis、ConfigMap、Secret、PVC 等 YAML。

待补：
- 把 `<YOUR_ORG>` 替换成真实 SWR 组织名。
- CCE 上 `kubectl get pods`、`kubectl get svc` 截图。
- ELB 公网 IP 访问 `/api/ping` 的浏览器或 curl 截图。

### 任务5 ConfigMap Volume

- `deploy/k8s/app/nginx-configmap.yaml` 已把完整 Nginx 配置放入 ConfigMap。
- `deploy/k8s/app/frontend-deployment.yaml` 已把 ConfigMap 挂载到 `/etc/nginx/conf.d`。
- 没有使用 `subPath`，因为 `subPath` 挂单文件时 ConfigMap 更新不会自动同步到容器内文件，不符合任务书要求。

待补：
- CCE 上 apply 后 exec 进前端 Pod：`cat /etc/nginx/conf.d/default.conf` 截图。
- 把 ConfigMap 里的后端端口临时改成错误值再 apply，验证 Pod 内文件变更的截图。

### 任务6 HPA

- `deploy/k8s/app/backend-hpa.yaml` 已按任务书写：`minReplicas=1`，`maxReplicas=4`，CPU 目标 60%。

待补：
- CCE 上 `kubectl top nodes` 截图。
- 压测期间 `kubectl get pods -w` 扩容截图。
- 停止压测后 Pod 缩回的截图。
- 如果没触发，补 `kubectl describe hpa backend-hpa` 和原因分析。

### B-1 并行算法实现

- `mpi/integral_serial.py` 是串行梯形法。
- `mpi/integral_mpi.py` 是阻塞 MPI 版，使用 `scatter` 分发区间、`reduce` 汇总积分。
- `docs/report-notes/mpi-communication.md` 已放通信示意素材。

待补：
- WSL 里安装 MPI 和 `mpi4py` 后跑串行/并行结果一致截图。

### B-2 性能测试与 Amdahl 分析

- `mpi/bench_mpi.py` 可按 1、2、4 进程各跑 3 次并生成 CSV。
- `mpi/plot_amdahl.py` 可根据 CSV 画实测加速比和 Amdahl 理论加速比双折线图。

待补：
- 真实运行产生的 `docs/report-notes/mpi-benchmark.csv`。
- 真实图表 `docs/report-notes/mpi-amdahl.png`。
- 报告里根据真实数据补差距分析。

### B-3 非阻塞通信优化

- `mpi/integral_mpi_nonblocking.py` 已用 `isend/irecv` 改写任务分发和结果回传。
- `mpi/compare_blocking_nonblocking.py` 可对比 4 进程下阻塞版和非阻塞版时间。

待补：
- 真实 4 进程对比截图。
- 根据真实时间写适用条件分析。

### C-1 分布式 AI 训练

- `ai-training/train_single.py` 是单机 MNIST CNN 训练脚本。
- `ai-training/train_ddp.py` 是 PyTorch DDP 版本。
- `ai-training/Dockerfile` 已准备训练镜像构建文件。
- `deploy/k8s/ai-training/mnist-single-job.yaml` 是单机基线 Job。
- `deploy/k8s/ai-training/mnist-ddp-job.yaml` 是 2 Worker Pod 的 DDP Indexed Job。
- `docs/report-notes/c1-distributed-ai-training.md` 已写专题主体草稿，真实时间和截图位置留待补充。

待补：
- 把 `<YOUR_ORG>` 替换成真实 SWR 组织名。
- 推送训练镜像到 SWR。
- CCE 上 2 Worker Pod 训练日志截图。
- 单机训练时间和分布式训练时间对比。
