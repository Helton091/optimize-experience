---
type: "Optimization"
title: "按目标节点重组 SplineConv 聚合"
description: "先按目标节点累计 basis×x 的槽位特征，再统一乘核权，可把多重入边的大矩阵点积合并；须用误差预算验证浮点重结合。"
tags: ["task.optimization", "topic.splineconv", "topic.reduction", "topic.sparse_graph"]
status: "stable"
sources: [{"resource":"https://gitcode.com/Zhanng-Whu/elec-ops-inspection/blob/f36ce9522ea84a30c5ce6e71ee7a473d53efff09/2026_elec_operator_competition/preliminary/submissioins/whu_Zhanng-Whu/code/splineconv/op_kernel/spline_conv_resident.h","role":"implementation"},{"resource":"https://github.com/Helton091/SpineConv/blob/984fce058894b6f3f9cf23b6a12d7e9d65925558/splineconv_template/op_kernel/spline_conv.cpp","role":"implementation"}]
created_at: "2026-11-17T11:29:26Z"
updated_at: "2026-11-17T11:29:26Z"
platforms: ["ascend910b"]
cann_versions: ["9.0.0"]
aliases: ["EXP-SPLINE-GROUP-01"]
---
# 按目标节点重组 SplineConv 聚合

## Summary

我们长期使用“每边先构造 `W_eff`，再做 `x@W_eff`，最后累加到目标节点”的顺序。公开常驻路径提供另一种顺序：先按目标节点累计每个核槽的 `basis×x`，再统一乘核权。多重入边因此可以共享一次大范围点积，而不是每边各做一次。

## Use When

- 同一目标节点有多条入边，且每边 `CIn×COut` 的核权加权与点积调用成本明显。
- 可以用链表、CSR 或等效结构按目标节点遍历入边。
- `K×CIn` 的槽位聚合缓冲可放入 UB，并有流式回退。

## Avoid When

- 几乎所有目标节点入度都为 1；此时没有跨边合并收益，新索引和缓冲可能净亏。
- 把浮点重结合当成逐位等价，或忽略高入度时的数值稳定性。
- 为实现分组而引入比原扫描更贵的建表和跨核同步。

## Signals

对同一目标节点，数学上可以写成：

```text
A[k, ci] = Σ_{e:dst=e_target} basis[e,k] × x[src[e],ci]
out[co]  = Σ_{k,ci} A[k,ci] × weight[k,ci,co]
```

这与逐边计算 `Σ_k basis[e,k]×weight[k]` 后再乘 `x` 在实数代数上等价，但浮点求和顺序不同。

公开 `SplineKernel::AccumulateEdge` 先在 `agg[k×CIn+ci]` 上累积，随后由 `FusedDotMatrix` 统一消费；我们的公开历史实现则为每条边构造 `CIn×COut` 的 `weff` 并立即归约。

## Method

1. 按目标节点建立入边链表或 CSR，明确无效边和自环的处理。
2. 只在 `K×CIn` 的槽位缓冲上累计 `basis×x`，避免每边构造完整的 `CIn×COut` 中间矩阵。
3. 对每个非空目标节点统一进行核权点积；`mean` 在聚合后只除一次有效入度。
4. `root_weight` 与 `bias` 仍在邻域聚合和 mean 之后叠加，不与显式自环混为一项。
5. 高入度时使用普通精度回退或补偿求和，并比较误差，而不是默认重结合无害。

## What To Verify

- 同一目标 1/2/多条入边、重复 `weight_index`、零基函数、重边、自环和孤立节点。
- `mean/add`、`root_weight/bias`、fp32/bf16，以及所有 `dim/degree/kernel_size` 组合。
- 与独立标量参考比较绝对/相对误差；不要要求不同求和顺序逐位一致。
- 比较逐边与按节点两种实现的实际向量调用数、UB 和最慢核时间。

## Evidence

固定版本公开代码证明该重组已被用于完整实现。我们的历史大档公开属性 `E=8` 很小，但小 `E` 不等于入度必为 1；是否采用应按实际重复目标分布测量。

本卡不宣称该路径是公开对照所有规模获胜的主因。公开大档主要走另一条按边局部核权路径；中档才直接体现这类常驻槽位聚合。

## Failure Bounds

当 `K×CIn` 缓冲过大、入度为 1 或建表成本超过共享点积收益时，应回退到逐边或流式路径。补偿求和也会新增多次向量操作，不能只按数学精度决定性能路径。

## Related Cards

- [按图 regime 选择执行骨架](sparse_graph_regime_dispatch.md)
- [稀疏图按命中边取局部核权](sparse_graph_local_weight_fetch.md)
- [归约慢时重构整条延迟链](restructure_reduction_latency_chain.md)
