# MPI 性能测试结果记录

测试环境：WSL，本地 `~/code/yjs-final`，使用 `.env/bin/python`、`mpiexec` 和 `mpi4py`。

固定问题规模：梯形法数值积分，`steps=10000000`。

运行命令：

```bash
cd ~/code/yjs-final/mpi
mpiexec -n 4 ../.env/bin/python integral_mpi.py --steps 10000000
../.env/bin/python bench_mpi.py --steps 10000000 --repeat 3 --mpiexec mpiexec
../.env/bin/python plot_amdahl.py
../.env/bin/python compare_blocking_nonblocking.py --steps 10000000 --mpiexec mpiexec
```

## B-1 结果一致性

4 进程 MPI 结果：

```text
method=mpi-blocking processes=4 steps=10000000 pi=3.141592653590 error=1.066e-14 time=0.259881
```

结果和圆周率参考值一致，误差在 `1e-14` 量级。

## B-2 性能测试

| 进程数 | 三次运行时间 / s | 平均时间 / s | 实测加速比 | Amdahl 理论值 |
|---:|---|---:|---:|---:|
| 1 | 0.700453, 0.674466, 0.707711 | 0.694210 | 1.000000 | 1.000000 |
| 2 | 0.391115, 0.358420, 0.369417 | 0.372984 | 1.861233 | 1.841016 |
| 4 | 0.216797, 0.216458, 0.222289 | 0.218515 | 3.176949 | 3.176949 |

按 4 进程实测加速比反推，可并行比例约为 `0.9136`。本地测试里 4 进程加速比较明显，但没有达到线性加速，主要原因是进程启动、任务分发、Reduce 汇总和进程同步仍有固定开销。

`bench_mpi.py` 生成的原始数据文件：

```text
docs/report-notes/mpi-benchmark.csv
docs/report-notes/mpi-benchmark.log
docs/report-notes/mpi-amdahl.png
```

这些文件当前被 `.gitignore` 忽略，提交报告时可以用截图或手动放到 `docs/screenshots/`。

## B-3 阻塞与非阻塞对比

4 进程对比结果：

```text
method=mpi-blocking processes=4 steps=10000000 pi=3.141592653590 error=1.066e-14 time=0.223851
method=mpi-nonblocking processes=4 steps=10000000 pi=3.141592653590 error=1.066e-14 time=0.243991
4-process comparison: blocking=0.223851s nonblocking=0.243991s
```

本次本地测试中非阻塞版本没有更快。这个结果合理：当前任务每个进程只接收一次区间、返回一次局部积分，通信量很小，可重叠的通信时间有限；非阻塞版本还引入了更多点对点请求管理开销。报告里可以说明，非阻塞通信更适合通信延迟较高、通信和计算能明显重叠、迭代次数较多的场景。
