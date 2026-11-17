---
type: "Optimization"
title: "稀疏图按命中边取局部核权，不为每个核预载全核"
description: "当边数和每边基函数槽数很少时，用 E×S 个实际核权矩阵替代每核 K 个核权矩阵的常驻缓存，并按总矩阵数、复用率和等待链选择。"
tags: ["task.optimization", "topic.data_movement", "topic.sparse_graph", "topic.splineconv"]
status: "stable"
sources: [{"resource":"https://gitcode.com/Zhanng-Whu/elec-ops-inspection/blob/f36ce9522ea84a30c5ce6e71ee7a473d53efff09/2026_elec_operator_competition/preliminary/submissioins/whu_Zhanng-Whu/code/splineconv/op_kernel/spline_conv_local_weights.h","role":"implementation"},{"resource":"https://github.com/Helton091/SpineConv/blob/984fce058894b6f3f9cf23b6a12d7e9d65925558/splineconv_template/op_kernel/spline_conv.cpp","role":"implementation"},{"resource":"https://github.com/Helton091/SpineConv/blob/984fce058894b6f3f9cf23b6a12d7e9d65925558/experiment_history/reference/log_phase4_lb.md","role":"evidence"}]
created_at: "2026-11-17T11:29:26Z"
updated_at: "2026-11-17T11:29:26Z"
platforms: ["ascend910b"]
cann_versions: ["9.0.0"]
aliases: ["EXP-SPLINE-WEIGHT-01"]
---
# 稀疏图按命中边取局部核权，不为每个核预载全核

## Summary

SplineConv 的一条边只使用 `S=(degree+1)^dim` 个基函数槽，而全核有 `K=∏kernel_size[d]` 个矩阵。稀疏小图中，让每个执行核都预载全部 `K` 个矩阵，可能比按实际命中边加载 `S` 个相关矩阵昂贵得多。

不要问“所有边合起来是否几乎覆盖全核”，先问“当前分工下，全核缓存和按需加载各发起多少次搬运、等待落在谁的关键路径上”。

## Use When

- `E` 很小，`S<K`，且大量执行核没有命中边或每个核只处理少量边。
- 每核整份 `weight` 的 UB 占用、MTE2 发射或首次使用等待已经可见。
- 能在加载前算出每条边的 `weight_index`，并有通用全量缓存回退。

## Avoid When

- 同一核对同一批核权有很高的跨边复用，或 `E×S ≥ 执行核数×K`。
- 按需加载会产生更多短 DMA、重复权重或串行等待，净成本反而更高。
- 还不能保证闭样条、负向取模、重复槽位和尾块的索引正确性。

## Signals

设执行核数为 `B`，每个核权矩阵含 `CIn×COut` 个元素：

- 全核常驻的矩阵搬运数约为 `B×K`。
- 按边局部加载的矩阵搬运数约为 `E×S`，还可按实际有效边、重复 `weight_index` 或节点内复用进一步去重。
- 除了数量，还必须记录 DMA 次数、单次字节数、UB 容量、缓存命中和首次消费前的等待。

公开 SplineConv 对照的大档属性为 `E=8`、`S=4`、`K=9`、`CIn=128`、`COut=16`。我们的稠密实现使用 16 核并逐核预载全核：

- 我们：`16×9=144` 个矩阵，合计 `16×72=1152 KiB`。
- 公开对照的 `SplineSparseLocalWeights::SingleDot`：每条有效边加载 4 个相关矩阵，合计 `8×4=32` 个矩阵、`8×32=256 KiB`。

这是 **4.5×** 的核权矩阵搬运数差异。它不是新实测的耗时分解，但足以推翻“因为 8 条边的槽位并集接近 9，所以按需加载一定没有收益”的论断。

## Method

1. 先计算每条边的 `S` 个 `weight_index`，只加载相关 `W[weight_index]`。
2. 用 `B×K` 与 `E×S` 写第一版成本预算，再加入重复边、复用率、DMA 固定成本和等待位置。
3. 给“每核全量缓存”和“按边局部加载”分别保留实现，按图规模与入度门控，不把一种策略写成平台定律。
4. 对重复核权可做小缓存或去重，但缓存建立成本必须计入；不要在未测量时增加复杂命中表。
5. 用完整实现做同窗口 A/B，分别报告核权流量、任务时长和精度。

## What To Verify

- `dim/degree/kernel_size/is_open_spline` 组合下，槽位与数学参考一致。
- `pseudo=1`、闭样条回绕、重复槽位、零基函数、重边、自环和孤立节点。
- 入度升高或 `E` 增大时能回到全量缓存，不发生 UB 溢出或短 DMA 风暴。
- 对照实现与当前实现的计时窗口、dtype、布局和核数均一致。

## Evidence

我们的公开历史代码在 `ProcessDense()` 入口对所有执行核发起 `K×CIn×COut` 的核权搬运，即使部分核没有命中边。公开对照的大档路径在 `SingleDot()` 内按边加载 4 个矩阵，并保留通用 `SplineKernel` 作为其他属性的回退。

上述字节数来自固定版本代码与公开属性记录的静态核算。公开 PR 与榜单队伍相对应，但没有公开哈希把 PR 的每个字节绑定到某次评测构建，因此不把这些静态差异写成已经独立复测的耗时因果。

## Failure Bounds

本卡证明的是一种可选数据结构，不保证“按需加载总是更快”。同一公开实现的中档反而使用 48 核全量缓存，说明核数、缓存复用和并行度可以改变最优选择。

## Related Cards

- [按图 regime 选择执行骨架，而非微调单一通用 kernel](sparse_graph_regime_dispatch.md)
- [按目标节点重组 SplineConv 聚合](splineconv_group_by_destination.md)
- [先写成本预算再写 kernel](write_cost_budget_before_kernel.md)
