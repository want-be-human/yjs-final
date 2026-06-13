import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default="../docs/report-notes/mpi-benchmark.csv")
    parser.add_argument("--out", default="../docs/report-notes/mpi-amdahl.png")
    args = parser.parse_args()

    rows = []
    with open(args.csv, encoding="utf-8") as fp:
        for row in csv.DictReader(fp):
            rows.append(
                {
                    "p": int(row["processes"]),
                    "speedup": float(row["speedup"]),
                    "amdahl": float(row["amdahl"]),
                }
            )

    fig, ax = plt.subplots(figsize=(7, 4.2), dpi=160)
    ax.plot([r["p"] for r in rows], [r["speedup"] for r in rows], marker="o", label="Measured speedup")
    ax.plot([r["p"] for r in rows], [r["amdahl"] for r in rows], marker="s", label="Amdahl speedup")
    ax.set_title("Figure B-2 Measured Speedup vs Amdahl Model")
    ax.set_xlabel("MPI processes")
    ax.set_ylabel("Speedup")
    ax.set_xticks([r["p"] for r in rows])
    ax.grid(True, alpha=0.3)
    ax.legend()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
