# 附加题 1 监控系统报告素材

监控系统使用 kube-prometheus-stack 部署 Prometheus 和 Grafana。Prometheus 负责按固定间隔主动拉取指标，Grafana 负责把指标画成面板。离线包已经提供 Chart 和镜像包，实际部署时需要把镜像推送到自己的 SWR，再替换 values 里的镜像地址。

Prometheus Pull 采集方式不是业务主动推数据，而是 Prometheus 根据服务发现结果定时访问每个 target 的 `/metrics` 接口。这样做的好处是采集周期、超时和失败状态都由 Prometheus 统一控制，监控目标挂掉时也能在 Prometheus 里直接看到 target down。

报告里可以解释的指标：

- `container_cpu_usage_seconds_total`：容器累计 CPU 使用时间，配合 `rate()` 可以看一段时间内的 CPU 使用速度。
- `container_memory_working_set_bytes`：容器当前实际使用的内存工作集，适合观察 Pod 是否接近内存限制。
- `node_cpu_seconds_total`：节点 CPU 在不同模式下的累计时间，可用于计算节点 CPU 利用率。
- `up`：Prometheus 对 target 的抓取状态，`1` 表示可抓取，`0` 表示失败。

需要补的真实截图：

- `helm list -n monitoring`。
- `kubectl get pods -n monitoring`。
- Grafana 节点 CPU 利用率折线图。
- Grafana Pod 内存使用柱状图。
- 如果 Dashboard 没数据，补 Prometheus targets 页面或 `kubectl logs` 排查截图。
