import argparse
import math
import time

from mpi4py import MPI


def f(x):
    return 4.0 / (1.0 + x * x)


def local_trap(start_index, count, h):
    if count <= 0:
        return 0.0

    left = start_index * h
    right = (start_index + count) * h
    total = 0.5 * (f(left) + f(right))
    for i in range(1, count):
        total += f((start_index + i) * h)
    return total * h


def split_work(total_steps, size):
    base = total_steps // size
    extra = total_steps % size
    chunks = []
    pos = 0
    for rank in range(size):
        count = base + (1 if rank < extra else 0)
        chunks.append((pos, count))
        pos += count
    return chunks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=10_000_000)
    args = parser.parse_args()

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    t0 = MPI.Wtime()
    chunks = split_work(args.steps, size) if rank == 0 else None

    # Scatter: rank 0 sends one interval slice to each process.
    start_index, count = comm.scatter(chunks, root=0)
    h = 1.0 / args.steps
    part = local_trap(start_index, count, h)

    # Reduce: every process sends its partial integral back to rank 0.
    result = comm.reduce(part, op=MPI.SUM, root=0)
    elapsed = MPI.Wtime() - t0

    if rank == 0:
        print(
            f"method=mpi-blocking processes={size} steps={args.steps} "
            f"pi={result:.12f} error={abs(math.pi - result):.3e} time={elapsed:.6f}"
        )


if __name__ == "__main__":
    main()
