# 成员 A 指导书

## 负责范围

成员 A 主要负责第一部分中的后端、Redis、CCE 基础环境、PVC 持久化，以及第二部分 MPI 的环境部署和数值积分基础实现。

所有编写、运行、测试和部署默认在 WSL 环境下完成。

对应课程设计任务书中的部分：

- 第一部分：任务1 应用容器化
- 第一部分：任务2 CCE 集群搭建
- 第一部分：任务3 应用部署
- 第一部分：任务4 持久化存储
- 第二部分方向 B：B-0 环境部署
- 第二部分方向 B：B-1 并行算法实现
- 附加题 C-1：分布式 AI 训练中的单机训练基线

## 第一部分任务要求

### 任务1：应用容器化

负责内容：

- 后端 Flask API。
- Redis 连接逻辑。
- 后端依赖文件。
- 后端 Dockerfile。
- 后端镜像构建、Tag、推送 SWR。
- 配合成员 B 完成本地联调。

文件位置：

- 后端代码和依赖文件放在 `app/backend/`。
- 后端 Dockerfile 放在 `app/backend/Dockerfile.backend`。
- 本地联调用 `docker-compose.yml`。
- 截图和报告素材放在 `docs/screenshots/` 或 `docs/report-notes/`。

注意事项：

- 后端 Dockerfile 要保留多阶段构建结构。
- 后端依赖中要加入至少 1 个自选 Python 包。
- SWR 截图必须包含镜像名称和 Tag。
- 本地联调截图要能看到后端日志收到请求。
- 这一任务需要和成员 B 联调，因为前端页面、Nginx 代理和 `docker compose` 需要一起验证。

实验记录提醒：

- 记录操作步骤摘要。
- 保存本地联调关键截图。
- 保存后端日志截图。
- 保存 SWR 镜像列表截图。
- 如果构建、推送或联调失败，要记录问题和解决方案。

### 任务2：CCE 集群搭建

负责内容：

- 创建或协助创建 CCE 集群。
- 配置 KubeConfig。
- 验证 Worker 节点状态。

文件位置：

- KubeConfig 不提交到仓库。
- 集群信息和截图素材放在 `docs/report-notes/` 或 `docs/screenshots/`。

注意事项：

- CCE 集群版本要大于或等于 1.27。
- Worker 节点数量至少 2 个。
- 截图中必须能看到节点状态为 Ready。
- 截图中必须包含 VERSION 列。
- 这个任务会影响成员 B 后续 Service、HPA、ConfigMap Volume 的验证，需要尽早完成。

实验记录提醒：

- 记录集群创建和 KubeConfig 配置的操作步骤摘要。
- 保存节点 Ready 截图。
- 记录节点规格和 Region。
- 如果 kubectl 连接失败，要记录原因和处理过程。

### 任务3：应用部署

负责内容：

- 后端 Deployment。
- Redis Deployment。
- 后端 ConfigMap。
- Redis Secret。
- 配合成员 B 完成 Service 暴露和访问验证。

文件位置：

- 第一部分应用部署 YAML 放在 `deploy/k8s/app/`。
- 后端和 Redis 的 Deployment、ConfigMap、Secret 都放在这个目录。
- 不要把真实 KubeConfig、AK、SK 或明文密码提交到仓库。

注意事项：

- 后端副本数必须为 2。
- 后端要配置 resources requests 和 limits。
- Redis 副本数为 1。
- Redis 内存限制不能超过 512Mi。
- 后端镜像必须来自 SWR。
- ConfigMap 要注入 Redis 地址。
- Secret 要注入 Redis 密码，不能直接明文暴露。
- 这一任务必须和成员 B 联调，因为 Service、ELB 公网访问和 `/api/ping` 验证由两边配置共同决定。

实验记录提醒：

- 第一部分实验记录中要写操作步骤摘要。
- 保存 Pod Running 截图。
- 保存后端和 Redis 部署状态截图。
- 记录部署中遇到的问题和解决方案。

### 任务4：持久化存储

负责内容：

- Redis PVC。
- Redis 挂载持久化目录。
- 验证 Redis Pod 删除重建后数据不丢失。

文件位置：

- Redis PVC 和带挂载配置的 Redis 部署文件放在 `deploy/k8s/app/`。
- 持久化验证截图放在 `docs/screenshots/`。

注意事项：

- PVC 状态必须为 Bound。
- 验证过程必须包含写入、删除 Pod、重建后查询三个阶段。
- 截图要能看清 key 的写入和读取结果。
- 删除 Pod 后要确认新的 Redis Pod 已经重新 Running。
- 这个任务需要和成员 B 确认 Redis Service 和部署状态，避免验证时连接到错误对象。

实验记录提醒：

- 记录 PVC 创建和 Redis 挂载的操作步骤摘要。
- 保存 PVC Bound 截图。
- 保存写入测试数据截图。
- 保存删除 Pod 后的截图。
- 保存重建后读取成功截图。
- 记录持久化验证中出现的问题和解决方案。

## 第二部分任务要求

### B-0：环境部署

负责内容：

- 部署 MPI Operator。
- 修改 MPIJob 配置。
- 运行示例 MPI 作业。
- 保存示例作业日志。

文件位置：

- MPI Operator 文件和 MPIJob YAML 放在 `deploy/k8s/mpi/`。
- 示例运行日志和截图放在 `docs/screenshots/` 或 `docs/report-notes/`。

注意事项：

- MPIJob 镜像要替换为教师提供的 mpi4py SWR 镜像。
- `slotsPerWorker` 和 `workerReplicas` 要符合任务书要求。
- 截图要能看到 Launcher 和 Worker Pod。
- 日志中要能看到 π 的估算值。
- 这个任务需要和成员 B 联调，因为 B-2、B-3 的性能测试依赖 MPI 环境可用。

### B-1：并行算法实现

负责内容：

- 数值积分串行版。
- 数值积分 MPI 并行版。
- 基础结果验证。

文件位置：

- 数值积分串行版、MPI 并行版和后续性能测试相关文件放在 `mpi/`。
- 通信示意图和结果截图放在 `docs/screenshots/` 或 `docs/report-notes/`。

注意事项：

- 本题选择“数值积分（梯形法）”。
- 串行版和并行版结果必须一致。
- MPI 通信原语需要有说明数据流向的注释。
- 报告中需要通信模式示意图，成员 B 会配合整理。
- 这个任务需要和成员 B 联调，因为 B-2 性能测试和 B-3 非阻塞优化会基于这部分代码继续做。

## 附加题 C-1：分布式 AI 训练

负责内容：

- 单机 MNIST CNN 训练基线。
- 记录单机训练时间。
- 协助成员 B 做单机和分布式训练时间对比。

文件位置：

- 单机训练代码放在 `ai-training/`。
- 分布式 AI 训练相关 K8s 文件放在 `deploy/k8s/ai-training/`。
- 训练日志、时间记录和截图放在 `docs/screenshots/` 或 `docs/report-notes/`。

注意事项：

- 附加题要求不少于 1500 字专题内容，成员 A 需要提供单机实验部分的真实结果。
- 单机训练时间要能和成员 B 的分布式训练时间对应。
- 截图或日志要能证明单机训练实际运行过。
- 这个任务需要和成员 B 联调，因为分布式训练对比必须使用同一套可比较的训练设置。

## 报告注意事项

成员 A 负责整理：

- 第一部分任务 1-4。
- 第二部分 B-0、B-1。
- 附加题中的单机训练基线。
- 云环境信息。

第一部分实验记录必须包含：

- 操作步骤摘要。
- 关键截图。
- 问题与解决方案。

报告质量评分注意：

- 截图要清晰。
- 关键字段要能看清，比如 Pod 名称、状态、返回值、版本号。
- 不要留空白截图。
- 总结和分析不能只写空泛描述，要结合实际运行结果。
