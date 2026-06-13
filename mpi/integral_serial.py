import argparse
import math
import time


def f(x):
    return 4.0 / (1.0 + x * x)


def trap(start, end, steps):
    h = (end - start) / steps
    total = 0.5 * (f(start) + f(end))
    for i in range(1, steps):
        total += f(start + i * h)
    return total * h


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=10_000_000)
    args = parser.parse_args()

    t0 = time.perf_counter()
    result = trap(0.0, 1.0, args.steps)
    elapsed = time.perf_counter() - t0

    print(f"method=serial steps={args.steps} pi={result:.12f} error={abs(math.pi - result):.3e} time={elapsed:.6f}")


if __name__ == "__main__":
    main()
