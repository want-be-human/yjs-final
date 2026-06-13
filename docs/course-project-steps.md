# 云计算技术课程设计完成步骤

来源：`课程设计任务书-final.pdf`

## 任务总览

这次课设满分 100 分，附加题最多额外 15 分。

必须完成三块：

- 第一部分：云计算平台搭建，50 分
- 第二部分：并行编程实战，40 分，Spark 和 MPI 二选一
- 实验报告，10 分

附加题自愿做：

- 监控系统，+5 分
- CI/CD 流水线，+5 分
- 前沿专题，+5 分

## 推荐路线

当前选择：

- 第二部分：方向 B，MPI 并行科学计算
- 算法题：数值积分（梯形法）
- 附加题：前沿专题，分布式 AI 训练
- 本地环境：WSL
- Helm 来源：老师给的 Helm 官网 `https://v3.helm.sh/zh/`

建议第二部分按方向 B：MPI 并行科学计算推进。

原因很直接：MPI 方向不太依赖教师给的 OBS 数据集，代码量可控，性能测试也容易解释。算法题建议选“数值积分（梯形法）”，比矩阵乘法和并行排序更稳。

## 第一部分：云计算平台搭建

目标是在华为云 CCE 上部署一套 `Flask 后端 API + Redis` 应用。

### 1. 准备云资源

需要完成：

- 注册并实名认证华为云账号
- 申请“智能基座”代金券，课程代码 `SCAI004712`
- 开通或使用这些服务：
  - SWR：保存 Docker 镜像
  - CCE：运行 Kubernetes 集群
  - ELB：暴露后端服务公网访问
  - OBS：Spark 方向可能会用，MPI 方向一般不需要

注意：实验结束后释放 CCE 节点和 ELB，避免继续计费。

### 2. 应用容器化

需要写或准备这些文件：

- `backend/app.py`
- `backend/requirements.txt`
- `backend/Dockerfile`
- `frontend/static/index.html`
- `frontend/nginx.conf`
- `frontend/Dockerfile`
- `docker-compose.yml`

要求：

- 后端使用 Flask
- 后端提供 `/api/ping` 接口，返回 `{"status":"ok"}`
- 后端连接 Redis
- `requirements.txt` 里除了 `flask`、`redis`，还要加至少 1 个自选 Python 包，比如 `requests`
- 前端首页必须包含自己的学号和姓名
- 本地用 `docker compose up` 联调成功
- 截图保留前端页面和后端日志
- 构建后端和前端镜像，并推送到华为云 SWR
- 截图保留 SWR 镜像列表，必须能看到镜像名和 Tag

### 3. 创建 CCE 集群

要求：

- Kubernetes 版本 >= 1.27
- 创建 2 个 Worker 节点
- 建议节点规格先用 2 vCPU / 4GB
- 网络插件默认 Yangtse CNI 即可
- 下载 KubeConfig，配置本地 `kubectl` 或使用 CloudShell

验收截图：

```bash
kubectl get nodes -o wide
```

截图里要能看到：

- Worker 节点数量 >= 2
- `STATUS` 为 `Ready`
- 包含 `VERSION` 列

### 4. 部署应用到 CCE

需要准备这些 YAML：

- `k8s/backend-deployment.yaml`
- `k8s/redis-deployment.yaml`
- `k8s/service.yaml`
- `k8s/configmap.yaml`
- `k8s/secret.yaml`

后端 Deployment 要求：

- `replicas: 2`
- 镜像来自 SWR
- 配置 `resources.requests`
- 配置 `resources.limits`
- 用 ConfigMap 注入 Redis 地址
- 用 Secret 注入 Redis 密码
- 加 `/api/ping` livenessProbe

Redis Deployment 要求：

- `replicas: 1`
- `limits.memory <= 512Mi`

Service 要求：

- 后端 Service 类型为 `LoadBalancer`
- 后端 Service 加注解 `kubernetes.io/elb.class: union`
- Redis Service 类型为 `ClusterIP`

ConfigMap 要求：

- `REDIS_HOST=redis-svc`
- `REDIS_PORT=6379`

Secret 要求：

- Redis 密码用 base64 编码
- 不要把明文密码写进 `data.password`

验收截图：

```bash
kubectl get pods
kubectl get svc
curl http://<ELB_IP>/api/ping
```

需要证明：

- 所有 Pod 都是 `Running`
- `/api/ping` 返回 `{"status":"ok"}`

### 5. Redis 持久化

需要准备：

- `k8s/redis-pvc.yaml`
- 修改 `redis-deployment.yaml`

要求：

- PVC 使用 `storageClassName: csi-disk`
- 建议容量 `10Gi`
- Redis 把 PVC 挂载到 `/data`

验收命令：

```bash
kubectl get pvc
kubectl exec -it <redis-pod> -- redis-cli
SET testkey "hello"
GET testkey
kubectl delete pod <redis-pod>
kubectl exec -it <new-redis-pod> -- redis-cli
GET testkey
```

截图要包含：

- PVC 状态为 `Bound`
- 写入 `testkey`
- 删除 Redis Pod
- 新 Pod 里还能读到 `"hello"`

### 6. ConfigMap Volume 挂载

目标是把 Nginx 反向代理配置改成 ConfigMap 文件挂载。

需要准备：

- `k8s/nginx-configmap.yaml`
- 修改前端 Deployment

要求：

- ConfigMap 里保存完整 `nginx.conf`
- 前端 Pod 挂载到 `/etc/nginx/conf.d/default.conf`
- 修改 ConfigMap 中后端端口，比如 `5000` 改成 `5001`
- `kubectl apply` 后进入前端 Pod 查看文件内容

验收命令：

```bash
kubectl exec -it <frontend-pod> -- cat /etc/nginx/conf.d/default.conf
```

报告里需要说明：

- `envFrom` 适合简单键值配置，比如 Redis 地址、端口
- Volume 挂载适合完整配置文件，比如 Nginx 配置
- 需要被程序按文件读取的配置更适合 Volume

### 7. HPA 弹性伸缩

需要准备：

- `k8s/backend-hpa.yaml`

要求：

- `minReplicas: 1`
- `maxReplicas: 4`
- CPU 目标利用率 60%

验收命令：

```bash
kubectl top nodes
kubectl apply -f k8s/backend-hpa.yaml
kubectl get hpa
kubectl get pods -w
ab -n 10000 -c 200 http://<ELB_IP>/api/ping
```

截图要包含：

- HPA 创建成功
- 压测时 Pod 从 1 个增加到 2 个或更多
- 停止压测后 Pod 缩回 1 个

报告里要分析：

- 扩容为什么有延迟
- 冷却时间为什么必要
- HPA 对节省资源有什么价值

## 第二部分：并行编程实战

Spark 和 MPI 二选一即可。

## 方向 A：Spark 大数据分析

适合愿意处理数据集的人。

需要完成：

- 安装 Spark Operator
- 修改 `sparkapplication.yaml`
- 使用教师提供的 PySpark SWR 镜像
- executor 数量设置为 2
- 跑通 `wordcount.py`
- 从教师提供的 OBS 数据集中选一个
- 做数据清洗
- 做至少 4 个统计查询
- 做 Pandas 和 PySpark 性能对比
- 画性能对比图
- 写 Amdahl 分析

难点：

- 依赖教师提供的 Spark Operator 离线包
- 依赖教师提供的 PySpark 镜像
- 依赖 OBS 数据集路径
- Spark on K8s 出错时排查成本较高

## 方向 B：MPI 并行科学计算

建议选择这个方向。

需要完成：

### B-0 环境部署

- 部署 MPI Operator
- 修改 `mpijob.yaml`
- 使用教师提供的 mpi4py SWR 镜像
- 跑通 `pi_mpi.py`
- 截图 Launcher Pod 日志，里面要有 π 估算值

### B-1 并行算法实现

三选一：

- 并行矩阵乘法
- 数值积分（梯形法）
- 并行排序（奇偶换序）

建议选数值积分。

需要写：

- 串行版代码
- MPI 并行版代码
- 对比输出，证明结果一致
- MPI 通信原语注释
- 通信模式示意图

### B-2 性能测试与 Amdahl 分析

要求：

- 固定问题规模，比如积分区间 `10^7`
- 1、2、4 个 MPI 进程分别运行
- 每种进程数运行 3 次
- 取平均运行时间
- 计算实测加速比
- 估算可并行比例 `f`
- 画“实测加速比 vs Amdahl 理论加速比”双折线图
- 分析通信开销、进程同步等原因

### B-3 非阻塞通信优化

要求：

- 至少一处通信改成 `comm.Isend` / `comm.Irecv`
- 对比 4 进程下阻塞版和非阻塞版运行时间
- 分析什么情况下非阻塞通信有效，什么情况下提升有限

## 附加题

不做也不影响基础 100 分。

### 监控系统，+5

需要：

- 使用 kube-prometheus-stack
- 部署 Prometheus + Grafana
- Dashboard 展示节点 CPU、Pod 内存
- 报告说明 Prometheus Pull 采集原理和至少 3 个指标含义

### CI/CD 流水线，+5

需要：

- GitHub Actions 或 GitLab CI
- 自动构建镜像
- 推送到 SWR
- 更新 K8s Deployment
- 截图流水线 Passed
- 截图 Deployment 镜像 Tag 已更新

### 前沿专题，+5

当前选择：分布式 AI 训练。

任务书里这一题要求：

- 用 Horovod 或 PyTorch DDP 在 K8s 上以 2 个 Worker Pod 训练 MNIST CNN
- 对比单机和分布式训练时间
- 报告解释 AllReduce 梯度同步机制
- 区分数据并行和模型并行
- 专题内容不少于 1500 字，含截图或代码

另外两个可选方向是：

- 分布式 AI 训练：Horovod 或 PyTorch DDP
- 边缘计算模拟：K3s + MQTT

既然已经选分布式 AI 训练，后续不用再考虑 K3s + MQTT。

## 最终报告结构

建议按这个结构写：

1. 封面：课程名、学号、姓名、班级、日期
2. 华为云环境信息：Region、CCE 版本、节点规格
3. 第一部分实验记录：任务 1 到任务 6
4. 第二部分实验记录：按 Spark 或 MPI 子任务写
5. 性能测试与 Amdahl 分析
6. 总结与收获，不少于 200 字
7. 附录：Dockerfile、YAML、核心 Python 代码，或者仓库链接

## 截图清单

第一部分：

- 本地 `docker compose up` 运行截图
- 前端页面截图，包含学号姓名
- 后端日志收到请求截图
- SWR 镜像列表截图，包含镜像名和 Tag
- `kubectl get nodes -o wide`
- `kubectl get pods`
- `/api/ping` 返回成功
- `kubectl get pvc`
- Redis 写入 `testkey`
- 删除 Redis Pod
- 新 Redis Pod 读取 `testkey`
- ConfigMap Volume 挂载后，Pod 内 `nginx.conf` 内容
- `kubectl top nodes`
- HPA 扩容截图
- HPA 缩容截图

第二部分，如果选 MPI：

- MPI Operator 部署结果
- `mpijob` 运行结果
- `pi_mpi.py` 日志输出 π
- 串行版和并行版结果一致
- 1、2、4 进程运行时间
- 性能图
- 阻塞版和非阻塞版时间对比

## 代码是否需要自己写

需要。

附录里的代码只是脚手架和示例，不够覆盖整个实验。

附录已经给了：

- Dockerfile 模板
- docker-compose 模板
- K8s Deployment / Service / ConfigMap / Secret / PVC / HPA 模板
- SparkApplication 模板
- `wordcount.py` 示例
- MPIJob 模板
- `pi_mpi.py` 示例

附录没有完整覆盖：

- Flask 后端业务代码
- Redis 读写逻辑
- 前端页面和 Nginx 反向代理完整项目结构
- 你自己的 SWR 镜像地址
- 你自己的 Secret 密码
- 真实 CCE 集群配置
- Redis PVC 挂载后的完整 Deployment
- ConfigMap Volume 版本的前端 Deployment
- Spark 数据清洗代码
- Spark SQL 统计分析代码
- Pandas vs PySpark 性能测试代码
- MPI 串行版算法代码
- MPI 并行版算法代码
- 非阻塞通信优化代码
- 性能测试脚本和画图代码
- 实验报告正文

所以附录够你起步，不够直接交。

## 我可以帮你完成的部分

只要你给出学号、姓名、班级，以及后续云资源信息，我可以直接帮你做：

- 搭建本地项目结构
- 写 Flask + Redis 后端
- 写 Nginx 前端页面
- 写 `docker-compose.yml`
- 写后端和前端 Dockerfile
- 写全部 K8s YAML
- 写 Redis PVC 版本
- 写 ConfigMap Volume 版本
- 写 HPA YAML
- 写 MPI 数值积分串行版和并行版
- 写非阻塞通信优化版
- 写性能测试脚本
- 写画图脚本
- 整理实验报告初稿
- 整理截图清单
- 根据真实截图补报告分析
- 排查本地 Docker、kubectl、Helm、K8s 报错

## 需要你自己完成的部分

这些我不能完全替你做，因为需要你的账号、云控制台或真实资源：

- 华为云账号注册和实名认证
- 申请智能基座代金券
- 创建 CCE 集群时的控制台操作
- 下载 KubeConfig
- 获取 SWR 组织名、Region、登录信息
- 在云控制台确认镜像、ELB、CCE、PVC 等资源状态
- 提供教师发的离线包：
  - Spark Operator Chart
  - MPI Operator YAML
  - PySpark 镜像地址
  - mpi4py 镜像地址
  - OBS 数据集路径，如果选 Spark
- 按学校要求提交邮件
- 最终报告里的个人总结最好你自己改一遍，避免太像模板

## linux-amd64 文件夹有什么用

当前 `linux-amd64` 文件夹里有：

- `helm`
- `LICENSE`
- `README.md`

这基本就是 Linux amd64 平台的 Helm 客户端。

Helm 的作用是安装和管理 Kubernetes Chart。这个实验里它主要可能用于：

- 安装 Spark Operator
- 安装 kube-prometheus-stack
- 安装其他老师提供的 Helm Chart 离线包

注意：

- 这个 `helm` 文件是 Linux amd64 可执行文件
- 你现在是在 Windows PowerShell 下，不能直接像 Windows `.exe` 那样运行它
- 如果你在 Linux 服务器、华为云 CloudShell、WSL 或 Linux ECS 里做实验，它就能派上用场
- 如果全程在 Windows 本地操作，建议安装 Windows 版 Helm，或者直接用 CloudShell

Windows 上可用这些方式安装 Helm：

```powershell
winget install Helm.Helm
```

或者用 Chocolatey：

```powershell
choco install kubernetes-helm
```

如果你用 CloudShell，通常更省事，很多 Kubernetes 工具已经配好。

## 下一步建议

先把本地代码做出来：

1. Flask + Redis + Nginx
2. docker compose 跑通
3. Docker 镜像能构建
4. 再去申请和配置华为云资源

这样后面上 CCE 时问题会少很多。
