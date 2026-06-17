# MPI 性能测试结果记录

测试环境：WSL，本地 `/mnt/d/desktop/云计算/yjs-final`，使用虚拟环境 `.env`、`mpiexec` 和 `mpi4py`。

固定问题规模：梯形法数值积分，`steps=10000000`。

运行命令：

```bash
cd /mnt/d/desktop/云计算/yjs-final
source .env/bin/activate
python mpi/integral_serial.py --steps 1000000
mpiexec -n 4 python mpi/integral_mpi.py --steps 1000000
cd mpi
python bench_mpi.py --steps 10000000 --repeat 3 --mpiexec mpiexec
python plot_amdahl.py
python compare_blocking_nonblocking.py --steps 10000000 --mpiexec mpiexec
```

## B-1 结果一致性

串行版和 4 进程 MPI 并行版已在 WSL 中完成一致性验证，并保存截图：

```text
docs/screenshots/mpi-b1-serial-vs-parallel-consistency.png
```

4 进程 MPI 结果示例：

```text
method=mpi-blocking processes=4 steps=10000000 pi=3.141592653590 error=1.066e-14
```

结果和圆周率参考值一致，误差在 `1e-14` 量级。

## B-2 性能测试

| 进程数 | 三次运行时间 / s | 平均时间 / s | 实测加速比 | Amdahl 理论值 |
|---:|---|---:|---:|---:|
| 1 | 0.718948, 0.776388, 0.807686 | 0.767674 | 1.000000 | 1.000000 |
| 2 | 0.380760, 0.383996, 0.375098 | 0.379951 | 2.020453 | 1.930346 |
| 4 | 0.212183, 0.194609, 0.231290 | 0.212694 | 3.609288 | 3.609288 |

按 4 进程实测加速比反推，可并行比例约为 `0.9639`。本地测试里 4 进程加速比较明显，但没有达到线性加速，主要原因是进程启动、任务分发、Reduce 汇总和进程同步仍有固定开销。

`bench_mpi.py` 生成的原始数据文件：

```text
docs/report-notes/mpi-benchmark.csv
docs/report-notes/mpi-benchmark.log
docs/report-notes/mpi-amdahl.png
```

其中 `mpi-amdahl.png` 是 Amdahl 图表。注意：这些生成文件当前被 `.gitignore` 忽略，提交报告时可以用截图或手动强制加入。

## B-3 阻塞与非阻塞对比

4 进程对比结果：

```text
已保存截图：docs/screenshots/mpi-b3-blocking-vs-nonblocking.png
```

本次本地测试中非阻塞版本不一定更快。这个结果合理：当前任务每个进程只接收一次区间、返回一次局部积分，通信量很小，可重叠的通信时间有限；非阻塞版本还引入了更多点对点请求管理开销。报告里可以说明，非阻塞通信更适合通信延迟较高、通信和计算能明显重叠、迭代次数较多的场景。
