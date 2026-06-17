# C-1 分布式 AI 训练记录草稿

本部分选择 PyTorch DDP 做 MNIST CNN 训练。模型结构不做复杂设计，只保留两层卷积、一个全连接隐藏层和输出层，重点放在单机训练和 2 个 Worker Pod 分布式训练的对比。这样任务足够小，能在课程 CCE 节点上跑完，也能把主要差异集中到数据划分、梯度同步和通信开销上。

单机基线使用 `ai-training/train_single.py`。脚本会读取 MNIST 训练集，在 CPU 或 GPU 上完成若干 epoch 训练，并输出总训练时间。分布式版本使用 `ai-training/train_ddp.py`，由 `torchrun` 拉起两个进程，每个 Worker 进程根据自己的 rank 和 world size 初始化进程组。数据集仍然是 MNIST，但 DataLoader 前面加了 `DistributedSampler`，每个 rank 只处理自己负责的数据切片，避免两个 Worker 重复训练同一批样本。

DDP 的核心同步发生在反向传播阶段。每个 Worker 先根据自己的 mini-batch 算出本地梯度，随后 DDP 自动对参数梯度做 AllReduce。可以理解成所有节点把梯度加起来，再把平均后的梯度发回所有节点。这样每个 Worker 在 `optimizer.step()` 前看到的是同一份平均梯度，所以模型参数能保持一致。这个过程不是把完整模型集中到某个节点再广播，而是通过通信库把梯度规约和分发合在一起完成。

这里采用的是数据并行，不是模型并行。数据并行是每个 Worker 都保存一份完整模型，只是输入数据不同，训练时同步梯度。模型并行则是把一个模型拆到多个设备或节点上。MNIST CNN 很小，没有必要做模型并行；如果强行拆模型，通信次数反而会更多，实验重点也会偏离课程要求。

K8s 部署文件放在 `deploy/k8s/ai-training/`。单机基线使用 `mnist-single-job.yaml`，分布式训练使用 `mnist-ddp-job.yaml`。分布式 Job 使用 Indexed Job，`completions=2`、`parallelism=2`，每个 Pod 通过 `JOB_COMPLETION_INDEX` 得到自己的 node rank。`mnist-ddp` 是 headless Service，给 `torchrun` 的 rendezvous 提供稳定地址。当前镜像地址为 `swr.cn-north-4.myhuaweicloud.com/yjs-final/mnist-ddp:v3`。

实际实验保持 epoch、batch size 和设备条件一致：单机和分布式都运行 2 个 epoch，batch size 都是 128，都使用 CPU。由于集群节点资源有限，训练 Job 的 requests 调整为较小值，保证能在 2 vCPU / 4 GiB 节点上完成调度。这个设置只影响 Kubernetes 调度和资源上限，不改变 PyTorch DDP 的训练逻辑。

本次新账号云上结果如下：

```text
单机：train_time=51.534s
2 Worker DDP：train_time=43.475s
加速比：51.534 / 43.475 = 1.19
```

本次 2 Worker DDP 比单机略快，但加速比不高。主要原因是 MNIST CNN 计算量较小，单个 batch 的前向和反向传播时间不长，而 2 个 Worker 之间还需要 rendezvous、DistributedSampler 分片和梯度 AllReduce。同步通信与调度开销抵消了一部分数据并行收益。报告里可以直接说明：这个实验主要证明 DDP 能在 K8s 上跑通，并观察到小模型、小数据集下通信开销明显；当模型更大、单步计算量更高、训练 epoch 更多时，分布式训练才更容易体现收益。

需要截图的位置：

- `kubectl get pods`，能看到 `mnist-ddp` 两个 Pod 同时运行或已完成。
- `kubectl logs job/mnist-single`，能看到单机训练时间。
- `kubectl logs job/mnist-ddp` 或 rank0 Pod 日志，能看到 DDP 的 `workers=2` 和训练时间。
- 如果失败，保存 `kubectl describe pod <pod>`，重点看镜像拉取、DNS、资源不足和 Python 依赖问题。
