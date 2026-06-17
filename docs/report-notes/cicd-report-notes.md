# 附加题 2 CI/CD 流水线报告素材

流水线目标是把应用做成“提交代码后自动构建镜像、推送到 SWR、更新 K8s Deployment”的流程。仓库使用 GitHub Actions，workflow 文件在 `.github/workflows/deploy.yml`。

GitHub 仓库需要配置 5 个 Repository secrets：

```text
SWR_REGISTRY=swr.cn-north-4.myhuaweicloud.com
SWR_ORG=yjs-final
SWR_USERNAME=cn-north-4@<AK>
SWR_PASSWORD=<SWR 登录指令里的临时 Token>
KUBE_CONFIG=<base64 后的 kubeconfig 内容>
```

`KUBE_CONFIG` 可以在 PowerShell 里生成：

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("D:\vsCode\python\yjs\yjs-final-cluster-kubeconfig.yaml"))
```

也可以在 WSL 里生成：

```bash
base64 -w 0 /mnt/d/vsCode/python/yjs/yjs-final-cluster-kubeconfig.yaml
```

报告说明点：

- 持续集成关注代码提交后的自动构建和检查，目的是尽早发现代码或镜像构建问题。
- 持续部署是在构建通过后，把新版本自动发布到目标 K8s 环境。
- GitOps 的核心是把期望状态写进 Git 仓库，集群部署结果以仓库中的声明式配置为准。

当前状态：

- workflow 已准备好，文件为 `.github/workflows/deploy.yml`。
- CCE 集群 `yjs-final-cluster` 已重新创建，kubeconfig 已能访问集群。
- 当前 SWR 组织为 `yjs-final`，不要再使用旧组织名。
- 如果 GitHub 里只配置了一个 `YJS_SECRET`，现有 workflow 还不能直接使用。需要按上面的 5 个名字分别配置，或者之后再把 workflow 改成解析单个 secret。

需要补的真实截图：

- GitHub Actions 中 `build-and-deploy` 运行成功的页面。
- SWR 中后端、前端镜像的新 tag。
- `kubectl get deployment backend frontend -o wide` 或 Deployment 详情，能看到镜像 tag 已更新。
- 浏览器或 curl 验证 `/api/ping` 能访问。

注意：

- `KUBE_CONFIG` 内容敏感，只能放 GitHub Secrets，不能提交到仓库。
- SWR 登录 token 有有效期，流水线运行时报认证失败时，需要重新生成并更新 `SWR_PASSWORD`。
