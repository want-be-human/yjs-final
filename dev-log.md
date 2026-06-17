# 开发日志

## 2026-06-12

- 阅读课程设计任务书，整理应用容器化、CCE 部署、Redis 持久化、ConfigMap Volume、HPA、MPI 和附加题的完成路线。
- 新增 `docs/course-project-steps.md`、`docs/team-work-division.md`、`docs/member-a-guide.md`、`docs/member-b-guide.md`。
- 将队友已有的应用代码整理到 `app/backend`、`app/frontend`，补出后续需要的 `deploy/k8s`、`mpi`、`ai-training`、`docs/screenshots` 等目录。
- 明确本地运行以 WSL 为准，Windows 只作为编辑环境。

## 2026-06-13

- 补齐应用容器化、本地 compose、K8s 基础 YAML、Redis Secret/PVC、Nginx ConfigMap、后端 HPA。
- 补齐 MPI 串行、阻塞 MPI、非阻塞 MPI、性能测试、Amdahl 画图和阻塞/非阻塞对比脚本。
- 补齐 C-1 PyTorch 单机训练和 DDP 训练脚本、训练镜像 Dockerfile、K8s Job。
- WSL 中完成 `docker compose config`、Python 语法检查、K8s YAML 解析、本地 `/api/ping` 联调。
- 对齐任务书脚手架文件名：`Dockerfile.backend`、`Dockerfile.frontend`、`docker-compose.yml`、`deployment.yaml`、`configmap.yaml`、`secret.yaml`、`mpijob.yaml`。

## 2026-06-14

- 检查离线包 README 和目录，确认包含 MPI Operator、`mpi4py-latest.tar`、`monitoring-all.tar`、`kube-prometheus-stack-83.7.0.tgz` 和监控 values。
- 将附加题 1 监控系统和附加题 2 CI/CD 流水线补入成员 B 指导书和分工文档。
- 新增 `.github/workflows/deploy.yml`，敏感值全部从 GitHub Secrets 读取。
- 新增监控部署说明、离线资源说明、监控报告素材和 CI/CD 报告素材。

## 2026-06-15 到 2026-06-16

- 旧账号中完成过一次 CCE、SWR、应用部署、Redis PVC、ConfigMap Volume、HPA、MPIJob、C-1 DDP 的云上验证。
- 旧账号结果已过期，只能作为报告思路和历史参考，不能继续作为当前交付环境。
- C-1 历史结果：单机 `35.509s`，2 Worker DDP `39.128s`，加速比 `0.9074`。小模型下 DDP 略慢，原因是同步和调度开销抵消了并行收益。

## 2026-06-17

- 新账号重新创建 CCE 集群 `yjs-final-cluster`，kubeconfig 已能访问。
- 当前区域为 `cn-north-4`，SWR 组织为 `yjs-final`。
- 获取并检查队友分支 `origin/tom-dev`，保留队友新增的训练镜像、MNIST 下载脚本和资源调优内容。
- 合并本地修改时统一切换到新 SWR 组织 `yjs-final`，不再使用旧组织名。
- MPI 仍按老师离线包路线处理：使用 `mpi4py:latest`，本仓库脚本通过 `mpi-scripts` ConfigMap 挂载。
- 去掉 `deploy/k8s/app/service.yaml` 中旧账号 ELB ID，避免新集群绑定失败。
- `.gitignore` 已忽略 kubeconfig、本地 config、临时登录信息和证书文件，避免误提交云凭据。

## 当前遗留

- 需要在新账号中重新 push 前端、后端、MPI、AI 训练和监控镜像。
- 需要重新部署应用、MPIJob、C-1 Job、监控系统，并补新账号截图。
- GitHub Actions 需要 5 个独立 Repository secrets；只配置 `YJS_SECRET` 时现有 workflow 不能直接运行。
- 实验完成后释放 CCE、节点、ELB、EIP、云硬盘等按需资源。

## 2026-06-17 新集群补充

- 新账号环境已完成应用、Redis PVC、ConfigMap Volume、HPA、MPIJob、C-1 单机/分布式训练和监控系统部署验证。
- 应用后端已通过 ELB 公网地址访问 `/api/ping`，Redis 状态为 `ok`。
- MPI 使用老师离线包的 `mpi4py:latest` 镜像，`mpi-pi` 和 `integral-mpi` 均已在 CCE 上运行成功。
- C-1 训练结果：单机 MNIST 2 epoch 为 `51.534s`，2 Worker DDP 为 `43.475s`，本次加速比约 `1.19`。
- 监控系统因 CCE 自带旧版 Prometheus Operator CRD 和新版 Chart 字段不兼容，最终采用 Chart 部署 Grafana、自建 `yjs-prometheus` 采集指标的方案，Grafana 已能查询节点 CPU 和 Pod 内存指标。
- 还没完成的是 GitHub Actions 真实 Passed 截图；现有 workflow 需要 5 个独立 Repository Secrets，只有 `YJS_SECRET` 不够。

## 2026-06-17 审查修正

- 移除 `deploy/k8s/app/service.yaml` 中固定 ELB ID，避免复用 YAML 时绑定到单个历史 ELB。
- `mpi/Dockerfile` 改为当前 `cn-north-4/yjs-final` 的 `mpi4py:latest` 镜像。
- README 同步新 C-1 训练结果和监控系统完成状态；剩余主要缺口仍是监控截图和 GitHub Actions 真实 Passed 证据。

## 2026-06-17 截图整理

- 清理 `screenshots/` 中旧 ELB、旧 SWR 组织、旧 C-1 训练时间和重复截图。
- 保留的截图按任务书章节编号重命名，例如 `2.2-...`、`2.7-...`、`3.3-B-...`。
- C-1、监控和 CI/CD 的最终截图还需要按当前云环境重新补齐，避免和报告里的新结果混用。
