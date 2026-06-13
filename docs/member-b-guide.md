# 成员 B 指导书

## 负责范围

成员 B 主要负责第一部分中的前端、Service 暴露、ConfigMap Volume、HPA 弹性伸缩，以及第二部分 MPI 的性能测试、Amdahl 分析、非阻塞通信优化和附加题监控系统、CI/CD 流水线、分布式 AI 训练主体。

成员 B 可以在 Windows 环境下结合编辑器和辅助工具编写代码，但运行、测试、构建镜像和部署统一在 WSL 环境下完成。

对应课程设计任务书中的部分：

- 第一部分：任务1 应用容器化
- 第一部分：任务3 应用部署
- 第一部分：任务5 ConfigMap Volume 挂载
- 第一部分：任务6 HPA 弹性伸缩
- 第二部分方向 B：B-1 并行算法实现
- 第二部分方向 B：B-2 性能测试与 Amdahl 分析
- 第二部分方向 B：B-3 非阻塞通信优化
- 附加题 1：监控系统
- 附加题 2：CI/CD 流水线
- 附加题 C-1：分布式 AI 训练

## 第一部分任务要求

### 任务1：应用容器化

负责内容：

- Nginx 前端页面。
- 前端 Dockerfile。
- 前端 Nginx 反向代理配置。
- 前端镜像构建、Tag、推送 SWR。
- 配合成员 A 完成本地联调。

文件位置：

- 前端页面放在 `app/frontend/static/`。
- Nginx 配置放在 `app/frontend/nginx.conf`。
- 前端 Dockerfile 放在 `app/frontend/Dockerfile.frontend`。
- 本地联调用 `docker-compose.yml`。
- 截图和报告素材放在 `docs/screenshots/` 或 `docs/report-notes/`。

注意事项：

- 前端首页必须包含学号和姓名，用于验收识别。
- SWR 截图必须包含镜像名称和 Tag。
- 本地联调截图要能证明前后端通信正常。
- 这一任务需要和成员 A 联调，因为前端访问依赖后端接口和 Redis 相关服务正常。

实验记录提醒：

- 记录操作步骤摘要。
- 保存前端页面截图。
- 保存本地联调截图。
- 保存前端镜像 SWR 截图。
- 如果 Nginx 代理或前后端通信失败，要记录问题和解决方案。

### 任务3：应用部署

负责内容：

- 后端 LoadBalancer Service。
- Redis ClusterIP Service。
- ELB 公网访问验证。
- Pod 和 Service 状态截图。

文件位置：

- Service、前端相关部署文件和应用暴露相关 YAML 放在 `deploy/k8s/app/`。
- 公网访问验证截图放在 `docs/screenshots/`。

注意事项：

- 后端 Service 类型必须为 LoadBalancer。
- 后端 Service 要添加华为云 ELB 注解。
- Redis Service 类型必须为 ClusterIP。
- `/api/ping` 必须能通过 ELB 公网 IP 访问。
- 截图要能证明 Pod Running，并能看到访问返回结果。
- 这一任务必须和成员 A 联调，因为 Service 访问依赖 A 的 Deployment、ConfigMap、Secret 和镜像部署正确。

实验记录提醒：

- 第一部分实验记录中要写操作步骤摘要。
- 保存 Pod Running 截图。
- 保存 Service 状态截图。
- 保存浏览器或 curl 访问 `/api/ping` 的截图。
- 记录访问失败、端口错误、镜像拉取失败等问题和解决方案。

### 任务5：ConfigMap Volume 挂载

负责内容：

- Nginx ConfigMap。
- 前端 Deployment 中的 ConfigMap Volume 挂载。
- 验证 Pod 内配置文件更新。
- 报告中说明 Volume 挂载和 envFrom 的区别。

文件位置：

- Nginx ConfigMap 和前端 Deployment 放在 `deploy/k8s/app/`。
- Pod 内配置文件验证截图放在 `docs/screenshots/`。

注意事项：

- ConfigMap 中要包含完整 Nginx 配置。
- ConfigMap 要以 Volume 形式挂载到指定 Nginx 配置路径。
- 修改 ConfigMap 后，要进入前端 Pod 验证配置文件已经更新。
- 评分中会看 Volume 挂载验证截图和原理说明。
- 这个任务需要和成员 A 联调，因为 Nginx 反向代理的后端地址和端口要与 A 的后端 Service 保持一致。

实验记录提醒：

- 记录 ConfigMap 创建、挂载、更新、验证的操作步骤摘要。
- 保存 Pod 内配置文件更新截图。
- 记录配置没有生效时的排查过程和解决方案。

### 任务6：HPA 弹性伸缩

负责内容：

- 后端 HPA。
- 指标服务验证。
- 压测。
- 扩容和缩容截图。
- HPA 分析说明。

文件位置：

- HPA YAML 放在 `deploy/k8s/app/`。
- 压测记录、扩容截图、缩容截图放在 `docs/screenshots/` 或 `docs/report-notes/`。

注意事项：

- HPA 要绑定后端 Deployment。
- 最小副本数为 1，最大副本数为 4。
- CPU 目标利用率为 60%。
- 要先确认 metrics 数据可用。
- 压测时要截图证明 Pod 数从 1 增加到 2 或更多。
- 停止压测后要截图证明 Pod 数缩回。
- 报告中要分析扩容延迟、冷却时间和降本价值。
- 这个任务需要和成员 A 联调，因为 HPA 扩缩容依赖后端 Deployment 的 resources 配置和 `/api/ping` 可压测。

实验记录提醒：

- 记录 HPA 创建、压测、扩容、缩容的操作步骤摘要。
- 保存 metrics 可用截图。
- 保存扩容截图。
- 保存缩容截图。
- 记录 HPA 未触发时的排查过程和解决方案。

## 第二部分任务要求

### B-1：并行算法实现

负责内容：

- 复核成员 A 的串行版和 MPI 并行版。
- 整理结果一致截图。
- 整理通信模式示意图。

文件位置：

- MPI 数值积分代码放在 `mpi/`。
- 通信示意图和结果一致截图放在 `docs/screenshots/` 或 `docs/report-notes/`。

注意事项：

- 串行版和并行版结果必须一致。
- 通信模式示意图是任务书明确要求的材料。
- 这个任务需要和成员 A 联调，因为性能测试和非阻塞优化都基于 A 的基础实现。

### B-2：性能测试与 Amdahl 分析

负责内容：

- 1、2、4 个 MPI 进程性能测试。
- 每种进程数运行 3 次并取平均。
- 计算实测加速比。
- 估算可并行比例。
- 绘制实测加速比和 Amdahl 理论加速比双折线图。
- 写差距原因分析。

文件位置：

- 性能测试和画图相关文件放在 `mpi/`。
- 性能数据、图表和分析素材放在 `docs/report-notes/`。
- 图表成品放在 `docs/screenshots/` 或报告素材目录中。

注意事项：

- 问题规模要固定。
- 运行次数要足够，任务书要求每种进程数运行 3 次取平均。
- 表格里要有平均运行时间、实测加速比、Amdahl 理论值。
- 图表要清晰，有标题和编号。
- 分析要结合通信开销、进程同步等原因，不能只写泛泛结论。
- 这个任务需要和成员 A 联调，因为测试对象来自 B-1 的数值积分实现，MPI 环境来自 B-0。

### B-3：非阻塞通信优化

负责内容：

- 将关键通信改为非阻塞模式。
- 对比 4 进程下阻塞版和非阻塞版运行时间。
- 保存对比截图。
- 写适用条件分析。

文件位置：

- 非阻塞通信版本放在 `mpi/`。
- 阻塞版和非阻塞版对比截图放在 `docs/screenshots/`。

注意事项：

- 必须能体现非阻塞通信改写。
- 对比必须使用 4 进程。
- 报告中要分析非阻塞通信何时有效、何时改善有限。
- 分析要从网络延迟和计算量比例角度写。
- 这个任务需要和成员 A 联调，因为非阻塞优化要基于基础 MPI 版本改写，并且要确认结果仍然正确。

## 附加题 C-1：分布式 AI 训练

负责内容：

- 分布式 MNIST CNN 训练。
- K8s 上 2 个 Worker Pod 训练。
- 记录分布式训练时间。
- 和成员 A 的单机训练时间对比。
- 写专题主体内容。

文件位置：

- 分布式训练代码放在 `ai-training/`。
- 分布式训练部署文件放在 `deploy/k8s/ai-training/`。
- 训练日志、时间对比和截图放在 `docs/screenshots/` 或 `docs/report-notes/`。

注意事项：

- 附加题选择的是 C-1 分布式 AI 训练。
- 要使用 Horovod 或 PyTorch DDP。
- 要在 K8s 上以 2 个 Worker Pod 训练 MNIST CNN。
- 要对比单机和分布式训练时间。
- 报告中要解释 AllReduce 梯度同步机制。
- 报告中要区分数据并行和模型并行。
- 专题内容不少于 1500 字。
- 截图和日志要能证明实验可运行。
- 这个任务需要和成员 A 联调，因为时间对比依赖 A 的单机训练基线。

## 附加题 1：监控系统

负责内容：

- 使用离线包中的 kube-prometheus-stack Helm Chart。
- 加载 `monitoring-all.tar`，把监控相关镜像重新打 tag 到个人 SWR。
- 修改监控 values 中的 `<region>` 和 `<your-organization>`。
- 在 CCE 上部署 Prometheus + Grafana。
- 整理 Grafana Dashboard 截图和指标说明。

文件位置：

- 离线资源在 `离线包/monitoring/`。
- 监控部署说明和 values 模板放在 `deploy/k8s/monitoring/`。
- 报告素材放在 `docs/report-notes/monitoring-report-notes.md`。
- 截图放在 `docs/screenshots/`。

注意事项：

- 不能把 SWR 临时 Token、AK、SK 或 KubeConfig 写进仓库。
- `monitoring-values.template.yaml` 只保留占位符，真实 Region 和组织名部署时再替换。
- Grafana 截图要至少包含节点 CPU 利用率折线图和各 Pod 内存使用柱状图。
- 报告中要说明 Prometheus Pull 采集原理，并解释至少 3 个指标含义。
- 这个任务需要成员 A 提供 CCE、SWR 权限和 KubeConfig。

实验记录提醒：

- 保存 `helm list -n monitoring` 截图。
- 保存 `kubectl get pods -n monitoring` 截图。
- 保存 Grafana Dashboard 截图。
- 如果 Dashboard 没数据，保存 Prometheus targets 或 Pod 日志排查截图。

## 附加题 2：CI/CD 流水线

负责内容：

- 维护 GitHub Actions workflow。
- 自动构建前端和后端镜像。
- 推送镜像到 SWR。
- 更新 K8s Deployment 镜像 tag。
- 整理流水线 Passed 截图和 Deployment 更新截图。

文件位置：

- Workflow 放在 `.github/workflows/deploy.yml`。
- 报告素材放在 `docs/report-notes/cicd-report-notes.md`。
- 截图放在 `docs/screenshots/`。

注意事项：

- 所有敏感信息都放 GitHub Secrets，不写进仓库。
- 需要的 Secrets：`SWR_REGISTRY`、`SWR_ORG`、`SWR_USERNAME`、`SWR_PASSWORD`、`KUBE_CONFIG`。
- 当前 workflow 默认更新 `deployment/backend` 和 `deployment/frontend`。
- 第一次运行前需要确保 CCE 上已经存在对应 Deployment。
- 报告中要说明持续集成、持续部署和 GitOps 的区别。
- 这个任务需要成员 A 提供 SWR 登录信息、KubeConfig 和云上 Deployment 验证。

实验记录提醒：

- 保存 GitHub Actions 全部阶段 Passed 截图。
- 保存 SWR 镜像 tag 截图。
- 保存 Deployment 镜像 tag 已更新截图。
- 保存更新后 `/api/ping` 仍可访问的截图。

## 报告注意事项

成员 B 负责整理：

- 第一部分任务 5-6。
- 第一部分任务 3 中 Service 和公网访问验证。
- 第二部分 B-2、B-3。
- 第二部分 B-1 的结果一致截图和通信示意图。
- 附加题 1 监控系统。
- 附加题 2 CI/CD 流水线。
- 附加题 C-1 分布式训练主体。

第一部分实验记录必须包含：

- 操作步骤摘要。
- 关键截图。
- 问题与解决方案。

报告质量评分注意：

- 截图必须清晰。
- 关键内容要能看清，比如 Pod 名称、状态、返回值、时间数据。
- 图表要有编号和标题。
- 性能分析要有量化数据。
- 不要只写概念，要结合真实运行结果。
