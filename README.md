# 云计算课程设计

本仓库用于云计算技术课程设计。

当前选择：

- 第二部分：方向 B，MPI 并行科学计算
- 算法题：数值积分（梯形法）
- 附加题：监控系统、CI/CD 流水线、C-1 分布式 AI 训练
- 开发和运行环境：WSL

## 目录

- `app/backend/`：Flask 后端和后端镜像构建文件
- `app/frontend/`：Nginx 前端页面、反向代理配置和前端镜像构建文件
- `deploy/k8s/app/`：第一部分应用部署相关 YAML
- `deploy/k8s/mpi/`：第二部分 MPIJob 和 MPI Operator 相关文件
- `deploy/k8s/monitoring/`：监控系统附加题部署说明和 values 模板
- `deploy/k8s/ai-training/`：附加题分布式 AI 训练相关部署文件
- `mpi/`：数值积分串行版、MPI 并行版、非阻塞优化版和性能测试文件
- `ai-training/`：MNIST 单机训练和分布式训练文件
- `docs/`：任务说明、分工、指导书、截图和报告素材

## 本地联调

在 WSL 中运行：

```bash
docker compose up --build
```

浏览器访问：

```text
http://localhost:8080
```

接口验证：

```bash
curl http://localhost:8080/api/ping
curl http://localhost:5000/api/info
```

查看后端日志：

```bash
docker compose logs -f backend
```

## 当前进度

`app/backend/`、`app/frontend/` 和 `docker-compose.yml` 已覆盖第一部分任务 1 的本地代码基础。
当前已在华为云华北-北京四创建 CCE 集群 `yjs-final-cluster`，并创建 SWR 组织 `yjs-final`。前后端镜像已推送：

```text
swr.cn-north-4.myhuaweicloud.com/yjs-final/yjs-backend:v1
swr.cn-north-4.myhuaweicloud.com/yjs-final/yjs-frontend:v1
swr.cn-north-4.myhuaweicloud.com/yjs-final/mpi4py:latest
```

云上第一部分当前进度：

- CCE 已有 3 个 Worker 节点，其中前 2 个为 2 vCPU / 4 GiB，后续因 HPA 和 Metrics Server 资源不足新增 1 个 2 vCPU / 8 GiB 节点。
- backend、frontend、Redis、PVC、ConfigMap、Secret 和 Service 已部署到 CCE。
- `backend-svc` 已绑定共享型 ELB，公网 IP 为 `114.116.194.77`。
- `curl http://114.116.194.77/api/ping` 已验证后端和 Redis 链路正常。
- Redis PVC 持久化验证已完成，删除 Redis Pod 后新 Pod 仍能读取测试 key。
- ConfigMap Volume 挂载和更新验证已完成，前端 Pod 内 Nginx 配置文件可通过 ConfigMap 更新。
- HPA 已完成扩容和缩容验证，压测时后端副本扩容到 4，停止压测后完成缩容。
- MPI Operator 已部署成功，`mpi-pi` 和 `integral-mpi` 都已在 CCE 上运行完成，`integral-mpi` 输出 `pi=3.141592653590`。
- 本地 MPI 已完成串并行结果一致性、1/2/4 进程性能测试、Amdahl 图和 4 进程阻塞/非阻塞对比。
- 附加题 C-1 已完成单机 MNIST CNN 与 2 Worker PyTorch DDP 训练对比：单机 `51.534s`，DDP `43.475s`，加速比约 `1.19`。
- 监控系统已部署：kube-prometheus-stack 提供 Grafana，自建 `yjs-prometheus` 采集指标，已能查询节点 CPU 和 Pod 内存指标。

后续还需要：

- 补齐监控系统截图：Helm release、monitoring Pod、Grafana 节点 CPU 折线图、Pod 内存图
- 配置 GitHub Actions Secrets，跑通 CI/CD 流水线
- 补 CI/CD 通过后的新镜像 tag、Deployment 镜像 tag 更新和 `/api/ping` 验证截图
- 实验完成后释放 CCE、EIP、ELB 和云硬盘，避免持续计费
