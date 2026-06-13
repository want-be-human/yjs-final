import random

from mpi4py import MPI


comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

samples = 1_000_000
local_count = 0

for _ in range(samples):
    x = random.random()
    y = random.random()
    if x * x + y * y <= 1.0:
        local_count += 1

# Reduce: workers send hit counts to rank 0, rank 0 sums them.
total = comm.reduce(local_count, op=MPI.SUM, root=0)

if rank == 0:
    pi = 4.0 * total / (samples * size)
    print(f"[{size} processes] pi ~= {pi:.6f}")
