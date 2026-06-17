# C-1 分布式 AI 训练记录草稿

本部分选择 PyTorch DDP 做 MNIST CNN 训练。模型结构不做复杂设计，只保留两层卷积、一个全连接隐藏层和输出层，重点放在单机训练和 2 个 Worker Pod 分布式训练的对比。这样做的好处是训练任务足够小，能在课程 CCE 节点上跑完，也能把主要差异集中到数据划分、梯度同步和通信开销上。

单机基线使用 `ai-training/train_single.py`。脚本会下载 MNIST 训练集，按 batch 读取数据，在 CPU 或 GPU 上完成若干 epoch 训练，并输出总训练时间。分布式版本使用 `ai-training/train_ddp.py`，由 `torchrun` 拉起两个进程，每个 Worker 进程拿到自己的 rank 和 world size 后初始化进程组。数据集仍然是 MNIST，但 DataLoader 前面加了 `DistributedSampler`，每个 rank 只处理自己负责的数据切片，避免两个 Worker 重复训练同一批样本。

DDP 的核心同步发生在反向传播阶段。每个 Worker 先根据自己的 mini-batch 算出本地梯度，随后 DDP 自动对参数梯度做 AllReduce。AllReduce 可以理解成“所有节点把梯度加起来，再把平均后的梯度发回所有节点”。这样每个 Worker 在 optimizer.step 之前看到的是同一份平均梯度，所以模型参数能保持一致。这个过程不是把完整模型集中到某一个节点再广播，而是通过通信库把梯度规约和分发合在一起完成。节点越多，单个节点处理的数据越少，但同步梯度的通信成本也会上升。

这里采用的是数据并行，不是模型并行。数据并行是每个 Worker 都保存一份完整模型，只是输入数据不同，训练时同步梯度。模型并行则是把一个模型拆到多个设备或节点上，比如前几层在一个节点、后几层在另一个节点，或者把一个很大的矩阵分片存放。MNIST CNN 很小，没有必要做模型并行；如果强行拆模型，通信次数反而会更多，实验重点也会偏离课程要求。

K8s 部署文件放在 `deploy/k8s/ai-training/`。单机基线用 `mnist-single-job.yaml`，分布式训练用 `mnist-ddp-job.yaml`。分布式 Job 使用 Indexed Job，`completions=2`、`parallelism=2`，每个 Pod 通过 `JOB_COMPLETION_INDEX` 得到自己的 node rank。`mnist-ddp` 是 headless Service，给 `torchrun` 的 rendezvous 提供稳定地址。实际镜像为 `swr.cn-north-4.myhuaweicloud.com/yjs-final-2023112473/mnist-ddp:v3`，镜像构建阶段已经把真实 MNIST 数据预下载到 `/work/data`，避免 CCE Pod 运行时访问 MNIST 官方下载源超时。

实际实验保持 epoch、batch size 和 CPU/GPU 条件一致：单机和分布式都运行 2 个 epoch，batch size 都是 128，都使用 CPU。由于集群节点资源有限，训练 Job 的 requests 调整为 `300m CPU / 768Mi`，limits 调整为 `1 CPU / 2Gi`，该设置只影响 Kubernetes 调度和资源上限，不改变 PyTorch DDP 的训练逻辑。

```text
单机：train_time=35.509s
2 Worker DDP：train_time=39.128s
加速比：35.509 / 39.128 = 0.9074
```

单机日志输出为 `mode=single dataset=mnist samples=60000 epochs=2 device=cpu train_time=35.509s`。分布式 rank 0 日志输出为 `mode=ddp dataset=mnist samples=60000 workers=2 epochs=2 device=cpu train_time=39.128s`。本次实验中 DDP 没有比单机更快，主要原因是 MNIST CNN 计算量较小，每个 batch 的前向和反向传播时间不长，而 2 个 Worker 之间需要进行 rendezvous、DistributedSampler 分片和梯度 AllReduce，同步通信与调度开销抵消了数据并行带来的计算分摊收益。

如果分布式没有更快，这不一定是错误。MNIST 数据量小，CNN 也小，单个 batch 的计算时间很短，AllReduce 和 rendezvous 的开销可能盖过并行收益。CCE 的 Pod 调度、镜像拉取、CPU 限额、网络延迟都会影响结果。报告里可以直接说明：这个实验主要证明 DDP 在 K8s 上可以跑通，并观察到小模型小数据集下通信开销明显；当模型更大、单步计算量更高、训练 epoch 更多时，分布式训练才更容易体现收益。

需要截图的位置：

- `kubectl get pods`，能看到 `mnist-ddp` 两个 Pod 同时运行。
- `kubectl logs job/mnist-single`，能看到单机训练时间。
- `kubectl logs job/mnist-ddp` 或 launcher/rank0 Pod 日志，能看到 DDP 的 `workers=2` 和训练时间。
- 如果失败，保存 `kubectl describe pod <pod>`，尤其看镜像拉取、DNS、资源不足和 Python 依赖下载问题。

已保存/建议保存的截图：

- `docs/screenshots/c1-mnist-single-pod-completed.png`
- `docs/screenshots/c1-mnist-single-log.png`
- `docs/screenshots/c1-mnist-ddp-pods-completed.png`
- `docs/screenshots/c1-mnist-ddp-log.png`
- 可选：`docs/screenshots/c1-mnist-jobs-complete.png`
