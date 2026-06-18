import argparse
import math

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
    tag_work = 11
    tag_result = 12

    t0 = MPI.Wtime()
    h = 1.0 / args.steps

    if rank == 0:
        chunks = split_work(args.steps, size)
        reqs = []
        for dest in range(1, size):
            # Isend：rank 0 非阻塞发送每个 worker 负责的积分区间分片。
            reqs.append(comm.isend(chunks[dest], dest=dest, tag=tag_work))

        own_start, own_count = chunks[0]
        own_part = local_trap(own_start, own_count, h)

        result_reqs = []
        for source in range(1, size):
            # Irecv：rank 0 提前挂起结果接收，等自己分片算完后再统一取回。
            result_reqs.append(comm.irecv(source=source, tag=tag_result))

        # Waitall：rank 0 确认任务分片都已发出，再开始汇总 worker 结果。
        MPI.Request.Waitall(reqs)
        total = own_part
        for req in result_reqs:
            total += req.wait()

        elapsed = MPI.Wtime() - t0
        print(
            f"method=mpi-nonblocking processes={size} steps={args.steps} "
            f"pi={total:.12f} error={abs(math.pi - total):.3e} time={elapsed:.6f}"
        )
    else:
        # Recv：worker 从 rank 0 接收自己负责的积分区间分片。
        start_index, count = comm.recv(source=0, tag=tag_work)
        part = local_trap(start_index, count, h)
        # Isend：worker 非阻塞发送本地积分结果回 rank 0。
        req = comm.isend(part, dest=0, tag=tag_result)
        req.wait()


if __name__ == "__main__":
    main()
