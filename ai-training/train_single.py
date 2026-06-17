import argparse
import time

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms


def load_dataset(args, transform):
    try:
        print(f"loading MNIST from {args.data_dir}", flush=True)
        return datasets.MNIST(args.data_dir, train=True, download=True, transform=transform), "mnist"
    except Exception as exc:
        if not args.allow_synthetic:
            raise
        print(f"MNIST download failed: {exc}", flush=True)
        print("falling back to offline MNIST-shaped synthetic data", flush=True)
        return datasets.FakeData(
            size=args.synthetic_size,
            image_size=(1, 28, 28),
            num_classes=10,
            transform=transform,
        ), "synthetic-mnist-shaped"


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


def train(args):
    device = torch.device("cuda" if torch.cuda.is_available() and not args.cpu else "cpu")
    transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))])
    dataset, dataset_name = load_dataset(args, transform)
    loader = DataLoader(dataset, batch_size=args.batch_size, shuffle=True, num_workers=2)

    model = Net().to(device)
    optimizer = optim.Adam(model.parameters(), lr=args.lr)

    t0 = time.perf_counter()
    for epoch in range(1, args.epochs + 1):
        model.train()
        total_loss = 0.0
        for data, target in loader:
            data = data.to(device)
            target = target.to(device)
            optimizer.zero_grad()
            output = model(data)
            loss = F.cross_entropy(output, target)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"epoch={epoch} loss={total_loss / len(loader):.4f}", flush=True)

    elapsed = time.perf_counter() - t0
    print(
        f"mode=single dataset={dataset_name} samples={len(dataset)} "
        f"epochs={args.epochs} device={device} train_time={elapsed:.3f}s",
        flush=True,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="./data")
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--lr", type=float, default=0.001)
    parser.add_argument("--cpu", action="store_true")
    parser.add_argument("--allow-synthetic", action="store_true")
    parser.add_argument("--synthetic-size", type=int, default=6000)
    args = parser.parse_args()
    train(args)


if __name__ == "__main__":
    main()
