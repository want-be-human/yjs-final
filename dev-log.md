# 开发日志

## 2026-06-12

- 阅读 `课程设计任务书-final.pdf`，整理课程设计完成路线。
- 新增 `course-project-steps.md`，记录任务拆分、截图清单、代码缺口、可协助部分和需要本人完成的部分。
- 检查 `linux-amd64`，确认里面是 Linux amd64 平台的 Helm 客户端，用于安装 Kubernetes Chart，比如 Spark Operator 或 kube-prometheus-stack。
- 确认实验选择：第二部分选 MPI 方向，算法题选数值积分；附加题选前沿专题里的分布式 AI 训练；本地环境准备用 WSL。
- 新增 `team-work-division.md`，按任务书的任务 1-6、B-0 到 B-3、C-1 附加题拆分两人工作，目标是 50% / 50%。
- 新增 `member-a-guide.md` 和 `member-b-guide.md`，分别给两名成员整理任务来源、评分注意事项、实验记录要求和联调节点。
- 将成员 A 发来的 `cloud-course-task1` 拆到仓库结构：`app/backend`、`app/frontend`、`compose.yaml`，并补出 `deploy/k8s`、`mpi`、`ai-training`、`docs/screenshots` 等后续位置。
- 更新成员 A/B 指导书，补充 WSL 运行前提和需要创建文件的位置。

遗留：

- 还没有生成实验代码，需要先确认学号、姓名、班级。
- 华为云 SWR、CCE、KubeConfig、教师离线包和镜像地址需要后续补齐。
