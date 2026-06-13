# C-1 分布式 AI 训练记录草稿

本部分选择 PyTorch DDP 做 MNIST CNN 训练。模型结构不做复杂设计，只保留两层卷积、一个全连接隐藏层和输出层，重点放在单机训练和 2 个 Worker Pod 分布式训练的对比。这样做的好处是训练任务足够小，能在课程 CCE 节点上跑完，也能把主要差异集中到数据划分、梯度同步和通信开销上。

单机基线使用 `ai-training/train_single.py`。脚本会下载 MNIST 训练集，按 batch 读取数据，在 CPU 或 GPU 上完成若干 epoch 训练，并输出总训练时间。分布式版本使用 `ai-training/train_ddp.py`，由 `torchrun` 拉起两个进程，每个 Worker 进程拿到自己的 rank 和 world size 后初始化进程组。数据集仍然是 MNIST，但 DataLoader 前面加了 `DistributedSampler`，每个 rank 只处理自己负责的数据切片，避免两个 Worker 重复训练同一批样本。

DDP 的核心同步发生在反向传播阶段。每个 Worker 先根据自己的 mini-batch 算出本地梯度，随后 DDP 自动对参数梯度做 AllReduce。AllReduce 可以理解成“所有节点把梯度加起来，再把平均后的梯度发回所有节点”。这样每个 Worker 在 optimizer.step 之前看到的是同一份平均梯度，所以模型参数能保持一致。这个过程不是把完整模型集中到某一个节点再广播，而是通过通信库把梯度规约和分发合在一起完成。节点越多，单个节点处理的数据越少，但同步梯度的通信成本也会上升。

这里采用的是数据并行，不是模型并行。数据并行是每个 Worker 都保存一份完整模型，只是输入数据不同，训练时同步梯度。模型并行则是把一个模型拆到多个设备或节点上，比如前几层在一个节点、后几层在另一个节点，或者把一个很大的矩阵分片存放。MNIST CNN 很小，没有必要做模型并行；如果强行拆模型，通信次数反而会更多，实验重点也会偏离课程要求。

K8s 部署文件放在 `deploy/k8s/ai-training/`。单机基线用 `mnist-single-job.yaml`，分布式训练用 `mnist-ddp-job.yaml`。分布式 Job 使用 Indexed Job，`completions=2`、`parallelism=2`，每个 Pod 通过 `JOB_COMPLETION_INDEX` 得到自己的 node rank。`mnist-ddp` 是 headless Service，给 `torchrun` 的 rendezvous 提供稳定地址。当前模板里的镜像地址还是 `<YOUR_ORG>` 占位，需要推送到 SWR 后替换成真实地址。

实际记录时建议保持 epoch、batch size 和 CPU/GPU 条件一致。比如单机和分布式都跑 2 个 epoch，batch size 都是 128，都使用 CPU，记录 `train_time=...s`。如果用 GPU，也要两边都写清楚 GPU 数量和型号。课程报告中不要只写“分布式更快”，要写具体时间。例如：

```text
单机：train_time=<待填>s
2 Worker DDP：train_time=<待填>s
加速比：<待填>
```

如果分布式没有更快，这不一定是错误。MNIST 数据量小，CNN 也小，单个 batch 的计算时间很短，AllReduce 和 rendezvous 的开销可能盖过并行收益。CCE 的 Pod 调度、镜像拉取、CPU 限额、网络延迟都会影响结果。报告里可以直接说明：这个实验主要证明 DDP 在 K8s 上可以跑通，并观察到小模型小数据集下通信开销明显；当模型更大、单步计算量更高、训练 epoch 更多时，分布式训练才更容易体现收益。

需要截图的位置：

- `kubectl get pods`，能看到 `mnist-ddp` 两个 Pod 同时运行。
- `kubectl logs job/mnist-single`，能看到单机训练时间。
- `kubectl logs job/mnist-ddp` 或 launcher/rank0 Pod 日志，能看到 DDP 的 `workers=2` 和训练时间。
- 如果失败，保存 `kubectl describe pod <pod>`，尤其看镜像拉取、DNS、资源不足和 Python 依赖下载问题。
