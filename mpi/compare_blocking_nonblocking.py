import argparse
import re
import shutil
import subprocess
import sys


TIME_RE = re.compile(r"time=([0-9.]+)")


def run(mpiexec, script, steps):
    cmd = [mpiexec, "-n", "4", sys.executable, script, "--steps", str(steps)]
    result = subprocess.run(cmd, check=True, text=True, capture_output=True)
    match = TIME_RE.search(result.stdout)
    if not match:
        raise RuntimeError(f"no time field in output: {result.stdout.strip()}")
    return float(match.group(1)), result.stdout.strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=10_000_000)
    parser.add_argument("--mpiexec", default=None)
    args = parser.parse_args()

    mpiexec = args.mpiexec or shutil.which("mpiexec") or shutil.which("mpirun")
    if not mpiexec:
        raise SystemExit("missing mpiexec/mpirun, install OpenMPI or MPICH in WSL first")

    blocking_time, blocking_line = run(mpiexec, "integral_mpi.py", args.steps)
    nb_time, nb_line = run(mpiexec, "integral_mpi_nonblocking.py", args.steps)

    print(blocking_line)
    print(nb_line)
    print(f"4-process comparison: blocking={blocking_time:.6f}s nonblocking={nb_time:.6f}s")


if __name__ == "__main__":
    main()
