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
