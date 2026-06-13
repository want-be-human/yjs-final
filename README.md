# 云计算课程设计

本仓库用于云计算技术课程设计。

当前选择：

- 第二部分：方向 B，MPI 并行科学计算
- 算法题：数值积分（梯形法）
- 附加题：C-1 分布式 AI 训练
- 开发和运行环境：WSL

## 目录

- `app/backend/`：Flask 后端和后端镜像构建文件
- `app/frontend/`：Nginx 前端页面、反向代理配置和前端镜像构建文件
- `deploy/k8s/app/`：第一部分应用部署相关 YAML
- `deploy/k8s/mpi/`：第二部分 MPIJob 和 MPI Operator 相关文件
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

`app/backend/`、`app/frontend/` 和 `compose.yaml` 已覆盖第一部分任务 1 的本地代码基础。

后续还需要：

- 在 WSL 中实际运行并截图
- 推送前后端镜像到 SWR 并截图
- 补齐第一部分 K8s YAML
- 补齐 MPI 数值积分代码
- 补齐分布式 AI 训练代码
- 云上部署、验证和截图
