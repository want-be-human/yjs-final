# 附加题 1 监控系统报告素材

本次监控部署一开始按任务书尝试使用离线包里的 `kube-prometheus-stack-83.7.0.tgz` 部署完整 Prometheus + Grafana。实际在 CCE 集群中遇到 Prometheus Operator CRD 版本不兼容：集群里已有旧版 CRD，新版 Chart 渲染出的 Prometheus/Operator 字段无法被当前 CRD 正常接受。直接覆盖 CRD 风险较高，可能影响集群已有监控 CRD 和后续资源创建，所以没有强行替换集群 CRD。

最终采用折中方案：仍使用 kube-prometheus-stack 部署 Grafana 页面和 Dashboard，用单独的 `yjs-prometheus` Deployment 采集集群指标，再把 Grafana datasource 指向 `yjs-prometheus`。这个方案保留了 Prometheus Pull 采集和 Grafana 可视化两部分核心验证，但报告里要如实说明它不是完整 Chart 原样部署成功。

已完成情况：

- `yjs-monitoring` Helm release 已部署，Grafana Pod 为 Running。
- `yjs-prometheus` 已部署，镜像来自个人 SWR：`swr.cn-north-4.myhuaweicloud.com/yjs-final/prometheus:v3.11.2`。
- Grafana datasource 已指向 `http://yjs-prometheus.monitoring:9090/`。
- 已通过 Grafana API 查询到 `node_cpu_seconds_total` 和 `container_memory_working_set_bytes`。
- 如果能找到当时完整 Chart 失败的终端输出，报告截图里建议补一张 `helm install/upgrade` 报错或 `kubectl describe` 事件，证明为什么改成当前方案。

Prometheus Pull 原理：

Prometheus 不要求业务主动上报指标，而是按配置里的 target 定时访问 `/metrics` 接口。每次采集是否成功会记录在 `up` 指标中，采集周期、超时、失败状态都由 Prometheus 统一控制。Kubernetes 场景下，Prometheus 可以结合服务发现找到节点、Pod、Service 等对象，再把指标按标签保存下来，Grafana 只负责查询和展示。

报告里可以说明的指标：

- `node_cpu_seconds_total`：节点 CPU 在不同运行状态下的累计时间，配合 `rate()` 可以计算节点 CPU 使用率。
- `container_memory_working_set_bytes`：容器当前实际使用的内存工作集，适合观察 Pod 是否接近内存限制。
- `container_cpu_usage_seconds_total`：容器累计 CPU 使用时间，配合 `rate()` 可以观察一段时间内的 CPU 使用速度。
- `up`：Prometheus 抓取 target 的状态，`1` 表示可抓取，`0` 表示抓取失败。

截图要求：

- `helm list -n monitoring`，证明监控组件部署成功。
- `kubectl get pods -n monitoring`，证明 Grafana、Prometheus、node-exporter、kube-state-metrics 正常运行。
- Grafana 节点 CPU 利用率折线图。
- Grafana 各 Pod 内存使用柱状图。
- 如 Dashboard 暂时没数据，补一张 Prometheus 查询 `node_cpu_seconds_total` 或 `container_memory_working_set_bytes` 成功的截图。
