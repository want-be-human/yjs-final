import argparse
import os
import time

import torch
import torch.distributed as dist
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.nn.parallel import DistributedDataParallel
from torch.utils.data import DataLoader
from torch.utils.data.distributed import DistributedSampler
from torchvision import datasets, transforms


class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 16, 3, 1)
        self.conv2 = nn.Conv2d(16, 32, 3, 1)
        self.fc1 = nn.Linear(4608, 64)
        self.fc2 = nn.Linear(64, 10)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.max_pool2d(F.relu(self.conv2(x)), 2)
        x = torch.flatten(x, 1)
        x = F.relu(self.fc1(x))
        return self.fc2(x)


def setup():
    backend = "nccl" if torch.cuda.is_available() else "gloo"
    dist.init_process_group(backend=backend)
    rank = dist.get_rank()
    world_size = dist.get_world_size()
    return rank, world_size


def train(args):
    rank, world_size = setup()
    use_cuda = torch.cuda.is_available() and not args.cpu
    if use_cuda:
        local_rank = int(os.environ.get("LOCAL_RANK", "0"))
        torch.cuda.set_device(local_rank)
        device = torch.device("cuda", local_rank)
    else:
        device = torch.device("cpu")

    transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))])
    dataset = datasets.MNIST(args.data_dir, train=True, download=True, transform=transform)
    dist.barrier()

    sampler = DistributedSampler(dataset, num_replicas=world_size, rank=rank, shuffle=True)
    loader = DataLoader(dataset, batch_size=args.batch_size, sampler=sampler, num_workers=2)

    model = Net().to(device)
    model = DistributedDataParallel(model)
    optimizer = optim.Adam(model.parameters(), lr=args.lr)

    t0 = time.perf_counter()
    for epoch in range(1, args.epochs + 1):
        sampler.set_epoch(epoch)
        total_loss = 0.0
        model.train()
        for data, target in loader:
            data = data.to(device)
            target = target.to(device)
            optimizer.zero_grad()
            output = model(data)
            loss = F.cross_entropy(output, target)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        avg = torch.tensor(total_loss / len(loader), device=device)
        dist.all_reduce(avg, op=dist.ReduceOp.SUM)
        avg = avg.item() / world_size
        if rank == 0:
            print(f"epoch={epoch} loss={avg:.4f}", flush=True)

    elapsed = time.perf_counter() - t0
    if rank == 0:
        print(f"mode=ddp workers={world_size} epochs={args.epochs} device={device} train_time={elapsed:.3f}s", flush=True)

    dist.destroy_process_group()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="/data")
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--lr", type=float, default=0.001)
    parser.add_argument("--cpu", action="store_true")
    args = parser.parse_args()
    train(args)


if __name__ == "__main__":
    main()
