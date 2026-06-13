# 两人分工建议

已选方案：

- 第二部分：方向 B，MPI 并行科学计算
- 算法题：数值积分（梯形法）
- 附加题：监控系统、CI/CD 流水线、C-1 分布式 AI 训练都尽量完成

原则：

- 两个人都要接触第一部分和第二部分，避免答辩时只有一个人说得清。
- 成员 A 偏云平台、后端、存储、MPI 环境。
- 成员 B 偏前端配置、弹性伸缩、MPI 性能分析、监控系统、CI/CD 流水线和分布式 AI 训练。
- 最终报告分工比例建议写 50% / 50%。

## 成员 A

### 第一部分：云计算平台搭建

任务1：应用容器化，10 分

- 写 Flask 后端 API。
- 写 Redis 连接逻辑。
- 写 `backend/requirements.txt`，加入至少 1 个自选 Python 包。
- 写后端多阶段 Dockerfile。
- 配合成员 B 完成 `docker-compose.yml` 本地联调。
- 负责后端镜像构建、Tag 和推送 SWR。

任务2：CCE 集群搭建，8 分

- 创建或协助创建 CCE 集群。
- 下载并配置 KubeConfig。
- 验证 `kubectl get nodes -o wide`。
- 保存 Worker 节点 Ready、VERSION 列截图。

任务3：应用部署，12 分

- 写后端 Deployment。
- 写 Redis Deployment。
- 写后端需要的 ConfigMap 和 Secret。
- 确认后端副本数、resources、Redis 密码注入正确。
- 配合成员 B 验证 `/api/ping`。

任务4：持久化存储，10 分

- 写 Redis PVC。
- 修改 Redis Deployment，把 PVC 挂载到 `/data`。
- 完成 `SET testkey`、删除 Pod、重新 `GET testkey` 的验证。
- 保存 PVC Bound 和持久化验证截图。

### 第二部分：MPI 并行科学计算

B-0：环境部署，10 分

- 部署 MPI Operator。
- 修改 `mpijob.yaml`，替换教师提供的 mpi4py SWR 镜像。
- 设置 `slotsPerWorker=2`、`workerReplicas=2`。
- 跑通 `pi_mpi.py` 示例。
- 保存 Launcher Pod 日志，里面要有 π 估算值。

B-1：并行算法实现，10 分

- 写数值积分串行版。
- 写基础 MPI 并行版，使用 Scatter 分发子区间，Reduce 汇总结果。
- 对每个 MPI 通信原语写必要注释，说明数据流向。
- 和成员 B 一起验证串行版、并行版结果一致。

### 附加题：C-1 分布式 AI 训练

- 写或整理单机 MNIST CNN 训练代码。
- 记录单机训练时间，作为分布式训练对比基线。
- 协助准备训练镜像 Dockerfile。

### 附加题：监控系统和 CI/CD 配合项

- 提供 CCE 集群、KubeConfig 和节点状态截图。
- 提供 SWR Region、组织名和镜像推送权限。
- 协助确认 GitHub Actions 使用的 `KUBE_CONFIG`、SWR 登录 Secrets 和 Deployment 名称。
- 协助验证流水线更新后端 Deployment 镜像 tag 后，`/api/ping` 仍能访问。

### 报告负责部分

- 第一部分任务 1-4。
- 第二部分 B-0、B-1。
- 附加题里的单机训练基线。
- 云环境信息：Region、CCE 版本、节点规格。

## 成员 B

### 第一部分：云计算平台搭建

任务1：应用容器化，10 分

- 写 Nginx 前端页面。
- `index.html` 中加入学号和姓名。
- 写前端 Dockerfile。
- 写或调整 Nginx 反向代理配置。
- 配合成员 A 完成 `docker-compose.yml` 本地联调。
- 负责前端镜像构建、Tag 和推送 SWR。

任务3：应用部署，12 分

- 写后端 LoadBalancer Service。
- 写 Redis ClusterIP Service。
- 添加华为云 ELB 注解 `kubernetes.io/elb.class: union`。
- 通过 ELB 公网 IP 验证 `/api/ping`。
- 保存 `kubectl get pods`、`kubectl get svc`、浏览器或 curl 访问截图。

任务5：ConfigMap Volume 挂载，5 分

- 新建 Nginx ConfigMap，data 里放完整 `nginx.conf`。
- 修改前端 Deployment，把 ConfigMap 挂载到 `/etc/nginx/conf.d/default.conf`。
- 修改 ConfigMap 中的后端端口后重新 apply。
- exec 进前端 Pod，截图验证配置文件已更新。
- 写 Volume 挂载和 envFrom 区别说明。

任务6：HPA 弹性伸缩，5 分

- 写后端 HPA YAML。
- 验证 `kubectl top nodes`。
- 使用 `ab` 或替代压测脚本压测 `/api/ping`。
- 保存 Pod 扩容截图和缩容截图。
- 写扩容延迟、冷却时间、降本价值分析。

### 第二部分：MPI 并行科学计算

B-1：并行算法实现，10 分

- 复核成员 A 的数值积分串行版和并行版。
- 补通信模式示意图。
- 整理串行版和并行版结果一致的截图。

B-2：性能测试与 Amdahl 分析，15 分

- 固定积分问题规模，比如 `10^7` 个点。
- 分别用 1、2、4 个 MPI 进程运行。
- 每种进程数运行 3 次，取平均。
- 计算实测加速比。
- 估算可并行比例 `f`。
- 绘制“实测加速比 vs Amdahl 理论加速比”双折线图。
- 分析实测与理论差距，比如通信开销、进程同步、容器调度影响。

B-3：非阻塞通信优化，5 分

- 将关键通信改成 `comm.Isend` / `comm.Irecv` 或等价非阻塞模式。
- 对比 4 进程下阻塞版和非阻塞版运行时间。
- 保存对比截图。
- 写非阻塞通信何时有效、何时改善有限的分析。

### 附加题：C-1 分布式 AI 训练

- 写 PyTorch DDP 或 Horovod 版本 MNIST CNN。
- 在 K8s 上用 2 个 Worker Pod 跑训练。
- 记录分布式训练时间。
- 和成员 A 的单机时间做对比。
- 保存训练 Pod、日志、时间对比截图。
- 写 AllReduce 梯度同步机制说明。
- 写数据并行和模型并行区别。
- 整理不少于 1500 字专题内容。

### 附加题：监控系统，+5 分

- 使用离线包中的 `kube-prometheus-stack` Chart 和 `monitoring-all.tar`。
- 把监控镜像加载、重新 tag 到个人 SWR，并配合成员 A 推送。
- 修改 `deploy/k8s/monitoring/monitoring-values.template.yaml` 中的 Region 和组织名。
- 在 CCE 上部署 Prometheus + Grafana。
- 保存监控 Pod 状态、Grafana 节点 CPU 折线图、Pod 内存柱状图截图。
- 写 Prometheus Pull 采集原理和至少 3 个指标含义。

### 附加题：CI/CD 流水线，+5 分

- 维护 `.github/workflows/deploy.yml`。
- 配置 GitHub Secrets 的说明和截图素材。
- 验证代码提交后自动构建前后端镜像、推送 SWR、更新 K8s Deployment。
- 保存 GitHub Actions Passed 截图和 Deployment 镜像 Tag 更新截图。
- 写持续集成、持续部署和 GitOps 的区别说明。

### 报告负责部分

- 第一部分任务 5-6，以及任务 3 的 Service 验证。
- 第二部分 B-2、B-3。
- 附加题监控系统、CI/CD 流水线和 C-1 分布式训练主体。
- 性能图表和 Amdahl 分析。

## 共同完成

- 本地 WSL 环境准备。
- Helm、kubectl、Docker、MPI 基础工具确认。
- 所有截图命名和归档。
- 报告合并、格式检查、图表编号。
- 最终仓库整理。
- 最终提交前互相讲一遍自己没主做的部分，避免答辩时说不清。

## 报告里可写的分工描述

成员 A：主要负责后端服务与 Redis 容器化、本地联调、SWR 后端镜像推送、CCE 集群配置、后端与 Redis 的 K8s 部署、PVC 持久化验证，以及 MPI Operator 部署、示例 MPIJob 运行和数值积分基础并行版实现；同时配合监控和 CI/CD 提供云资源、KubeConfig、SWR 权限和部署验证。

成员 B：主要负责前端 Nginx 页面与反向代理配置、前端镜像推送、Service 暴露、ConfigMap Volume 挂载、HPA 弹性伸缩验证、MPI 性能测试与 Amdahl 分析、非阻塞通信优化，以及监控系统、CI/CD 流水线和分布式 AI 训练附加题。

共同完成实验报告整合、截图检查、问题排查和最终提交。分工比例：成员 A 50%，成员 B 50%。
