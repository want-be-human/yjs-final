# 附加题 2 CI/CD 流水线报告素材

流水线目标是把第一部分应用做成“代码提交 -> 自动构建镜像 -> 推送 SWR -> 更新 K8s Deployment”的流程。仓库使用 GitHub Actions，workflow 文件在 `.github/workflows/deploy.yml`。

需要在 GitHub 仓库里配置 Secrets：

```text
SWR_REGISTRY=swr.cn-north-4.myhuaweicloud.com
SWR_ORG=yjs-final-2023112473
SWR_USERNAME=<region>@<AK>
SWR_PASSWORD=<SWR 登录指令里的临时 Token>
KUBE_CONFIG=<base64 后的 kubeconfig 内容>
```

`KUBE_CONFIG` 建议在 WSL 里生成：

```bash
base64 -w 0 ~/.kube/config
```

报告说明点：

- 持续集成关注代码提交后的自动构建和检查，目的是尽早发现代码或镜像构建问题。
- 持续部署是在构建通过后，把新版本自动发布到目标环境。
- GitOps 的核心是把期望状态写进 Git 仓库，集群部署结果以 Git 中的声明式配置为准。

需要补的真实截图：

- GitHub Actions 每个阶段 Passed。
- SWR 中新 tag 的后端和前端镜像。
- `kubectl get deployment backend frontend -o wide` 或 `kubectl describe deployment`，能看到镜像 tag 已更新。
- 浏览器或 curl 验证新部署仍能访问 `/api/ping`。

当前云资源状态：

- CCE 集群 `yjs-final-cluster` 已创建，WSL 中 `kubectl get nodes -o wide` 已能看到 2 个 Ready 节点。
- SWR 组织 `yjs-final-2023112473` 已创建。
- `yjs-backend:v1` 和 `yjs-frontend:v1` 已手动推送到 SWR，可作为首次部署和后续 CI/CD 对照基线。

注意：

- `KUBE_CONFIG` 来自公网访问版 kubeconfig，内容敏感，只能放 GitHub Secrets，不能提交到仓库。
- SWR 临时登录指令有效期有限，若流水线运行时过期，需要重新生成并更新 `SWR_PASSWORD`。
