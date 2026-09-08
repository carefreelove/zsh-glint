# Performance / 性能报告

[Home](../README.md) · [中文首页](../README.zh-CN.md)

## What changed

v0.1 iterated over a shell-expanded copy of the candidate array on every lookup. v0.2 uses Zsh's native array search with escaped literal prefixes, then caches the most recent query. A history refresh invalidates the query cache. Changing the effective length limits also prevents reusing an incompatible result. Ranking and matching behavior are unchanged.

v0.1 每次查询都展开候选数组并通过 Shell 循环查找。v0.2 改用 Zsh 原生数组搜索，将用户前缀中的模式字符转义，并缓存最近一次查询结果。刷新历史会使查询缓存失效，长度配置改变时也不会复用不适用的结果。排序和匹配语义保持不变。

## Recorded results

Recorded on **2026-09-08**, macOS arm64, `zsh 5.9 (arm64-apple-darwin25.0)`. Values are **median milliseconds**, using 30 measured lookups per scenario. Background load was not controlled. These are illustrative local measurements, not a latency guarantee or a comparison with other plugins.

| Candidates | Scenario | v0.1 | v0.2 |
| ---: | --- | ---: | ---: |
| 1,000 | First candidate matches / 首条命中 | 0.2825 | 0.0331 |
| 1,000 | Last candidate matches / 末条命中 | 2.2830 | 0.1731 |
| 1,000 | Cold miss / 首次未命中 | 2.2125 | 0.1010 |
| 1,000 | Repeated miss / 重复查询未命中 | 2.2005 | 0.0230 |
| 10,000 | Cold miss / 首次未命中 | 22.2905 | 0.7360 |
| 100,000 | Cold miss / 首次未命中 | 220.5359 | 7.1665 |
| 100,000 | Last candidate matches / 末条命中 | 227.5280 | 13.7265 |

The default cache limit is **1,000 entries**. Larger rows intentionally stress larger candidate arrays; they are not the default configuration. Cold scenarios invalidate the query cache before each sample. Repeated scenarios reuse a warmed query. Synthetic commands are unique and follow `echo job-NNNNNN --verbose`.

默认候选缓存上限为 **1,000 条**。更大的行用于压力测试，不代表默认配置。首次查询场景会在每次采样前清除查询缓存；重复查询场景复用已缓存的结果。合成命令采用 `echo job-NNNNNN --verbose` 格式。

History refresh is measured separately: with **100,000 loaded history entries** and a **1,000-entry cache limit**, median refresh took **39.76 ms before** and **40.64 ms after** (5 samples). The refresh algorithm was not optimized in this release; sorting still depends on the total loaded history size. It runs at prompt boundaries, not on each keystroke.

历史刷新单独测量：加载 100,000 条历史、缓存上限为 1,000 条时，刷新中位耗时由 39.76 ms 变为 40.64 ms，共 5 次采样。本版本没有优化刷新算法，排序成本仍随全部已加载历史增长；刷新发生在新 prompt 出现前，不在每次按键时执行。

Measurements exclude startup, terminal rendering, and `compinit`. Raw reports include sample counts and p95 values: [before](benchmark-before.json), [after](benchmark-after.json). The baseline is commit `172541d`, which reports plugin version `0.1.0`; the optimized code is in release `v0.2.0`.

## Reproduce

```sh
python3 scripts/benchmark.py --output /tmp/glint-after.json
git show 172541d:zsh-glint.plugin.zsh > /tmp/glint-before.plugin.zsh
python3 scripts/benchmark.py --plugin /tmp/glint-before.plugin.zsh --output /tmp/glint-before.json
```

The script creates isolated temporary Zsh history, sets its own benchmark configuration, and does not read or write your personal history file. CI runs a small benchmark smoke check to catch broken workloads; it does not enforce timing thresholds on shared runners.

脚本使用隔离的临时 Zsh 历史和固定配置，不读写你的个人历史文件。CI 只运行小规模基准冒烟检查，确认场景可执行；共享 runner 上不设硬性耗时阈值。
