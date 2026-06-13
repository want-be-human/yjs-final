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
            # Isend: rank 0 sends each worker its interval without waiting one by one.
            reqs.append(comm.isend(chunks[dest], dest=dest, tag=tag_work))

        own_start, own_count = chunks[0]
        own_part = local_trap(own_start, own_count, h)

        result_reqs = []
        for source in range(1, size):
            # Irecv: rank 0 posts result receives early, then waits after its own work.
            result_reqs.append(comm.irecv(source=source, tag=tag_result))

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
        start_index, count = comm.recv(source=0, tag=tag_work)
        part = local_trap(start_index, count, h)
        # Isend: worker returns the partial result while rank 0 already waits for all results.
        req = comm.isend(part, dest=0, tag=tag_result)
        req.wait()


if __name__ == "__main__":
    main()
