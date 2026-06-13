import argparse
import csv
import re
import shutil
import subprocess
import sys
from pathlib import Path


TIME_RE = re.compile(r"time=([0-9.]+)")


def run_once(mpiexec, processes, steps, script):
    cmd = [mpiexec, "-n", str(processes), sys.executable, script, "--steps", str(steps)]
    result = subprocess.run(cmd, check=True, text=True, capture_output=True)
    match = TIME_RE.search(result.stdout)
    if not match:
        raise RuntimeError(f"no time field in output: {result.stdout.strip()}")
    return float(match.group(1)), result.stdout.strip()


def amdahl(p, f):
    return 1.0 / ((1.0 - f) + f / p)


def estimate_f(s4):
    if s4 <= 1:
        return 0.0
    # S = 1 / ((1 - f) + f / p)
    f = (1.0 - 1.0 / s4) / (1.0 - 1.0 / 4.0)
    return max(0.0, min(0.999, f))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=10_000_000)
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--out", default="../docs/report-notes/mpi-benchmark.csv")
    parser.add_argument("--script", default="integral_mpi.py")
    parser.add_argument("--mpiexec", default=None)
    args = parser.parse_args()

    mpiexec = args.mpiexec or shutil.which("mpiexec") or shutil.which("mpirun")
    if not mpiexec:
        raise SystemExit("missing mpiexec/mpirun, install OpenMPI or MPICH in WSL first")

    rows = []
    raw_lines = []
    baseline = None

    for p in (1, 2, 4):
        times = []
        for i in range(args.repeat):
            elapsed, line = run_once(mpiexec, p, args.steps, args.script)
            times.append(elapsed)
            raw_lines.append(f"p={p} run={i + 1}: {line}")
        avg = sum(times) / len(times)
        if baseline is None:
            baseline = avg
        rows.append({"processes": p, "avg_time": avg, "speedup": baseline / avg})

    f = estimate_f(rows[-1]["speedup"])
    for row in rows:
        row["amdahl"] = amdahl(row["processes"], f)
        row["parallel_fraction"] = f

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=["processes", "avg_time", "speedup", "amdahl", "parallel_fraction"])
        writer.writeheader()
        writer.writerows(rows)

    raw_path = out.with_suffix(".log")
    raw_path.write_text("\n".join(raw_lines) + "\n", encoding="utf-8")
    print(f"wrote {out}")
    print(f"wrote {raw_path}")


if __name__ == "__main__":
    main()
