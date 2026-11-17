---
type: "Optimization"
title: "按图 regime 选择执行骨架，而非微调单一通用 kernel"
description: "稀疏小图的核数、边归属、核权策略和清零角色应随 E/N、K/S、入度和 UB 联合分派；旧骨架上的核数与负结果不能外推。"
tags: ["task.optimization", "topic.sparse_graph", "topic.specialization", "topic.scheduling"]
status: "stable"
sources: [{"resource":"https://gitcode.com/Zhanng-Whu/elec-ops-inspection/blob/f36ce9522ea84a30c5ce6e71ee7a473d53efff09/2026_elec_operator_competition/preliminary/submissioins/whu_Zhanng-Whu/code/splineconv/op_host/spline_conv.cpp","role":"implementation"},{"resource":"https://github.com/Helton091/SpineConv/blob/984fce058894b6f3f9cf23b6a12d7e9d65925558/splineconv_template/op_host/spline_conv.cpp","role":"implementation"},{"resource":"https://gitcode.com/cann/elec-ops-inspection/pull/142","role":"evidence"}]
created_at: "2026-11-17T11:29:26Z"
updated_at: "2026-11-17T11:29:26Z"
platforms: ["ascend910b"]
cann_versions: ["9.0.0"]
aliases: ["EXP-SPLINE-REGIME-01"]
---
# 按图 regime 选择执行骨架，而非微调单一通用 kernel

## Summary

公开对照并不是用一个“各方面都更少”的通用 kernel 获胜。它根据图 regime 选择不同的并行度、数据所有权和核权策略：小档绕开通用入口，中档用高并行常驻路径，大档用按边局部核权路径。

我们长期在同一稠密骨架内比较核数、tile 数、队列和单项 API，得到的局部最优不能约束这些新骨架。

## Use When

- `E≪N`，大量输出为零，且不同规模下的主要成本发生切换。
- 同一核数公式同时用于 `E=1`、`E≈CIn` 和 `K>S` 的图，却没有逐 regime 的成本模型。
- 多种“已否决”优化都只在同一所有权和调度结构下测试过。

## Avoid When

- 只是按公开 `N` 写魔术分支，没有可解释的触发条件和通用回退。
- 把某个快路径在公开点上的成绩当成全形状正确性或性能证据。
- 多写大量 kernel 副本，却没有共享数学参考和分派测试。

## Signals

公开属性与我们固定版本代码可确定以下分派。这里列的是代码事实，不是重新上机测得的独立收益：

| 公开负载 | 我们的稠密形态 | 公开对照的实际候选路径 | 关键差异 |
|---|---|---|---|
| 小：`N=16/15, E=1, CIn=8, K=4` | 8 核、15/16 个 dst tile、每核全量核权 | `SINGLE` 的 raw/staged 单边实现 | 跳过完整通用元数据；只有实际 owner 加载核权 |
| 中：`N=64/50, E=4, CIn=32, K=9` | 8 核、32/25 个 tile，逐 tile 扫 4 边 | `SplineKernel` 常驻路径，48 核、每核至多 2 节点 | 更高并行度；按节点链表聚合，再进行槽位融合点积 |
| 大：`N=256/200, E=8, CIn=128, K=9` | 16 核、64/50 个 tile，逐 tile 扫 8 边 | `RunSparseLocalWeights`，8 核、按边加载 4 个相关核权 | 核权流量和扫描结构同时改变 |

特别注意：公开中档的 `K=9` 使 `[2,2]` 专用 sparse 分支不会命中；公开大档的 `K=9` 也不是走 `[2,2]` 的 wide-owner。阅读对照代码时必须先沿 host 条件求出实际路径，不能把所有实现的亮点混在一张“冠军架构”里。

## Method

1. 用 `E/N`、`K/S`、入度分布、dtype、可选输入和 UB 余量定义 regime，而不是只按 `N` 分档。
2. 分别计算所有权成本：dst-tile 扫描约为 `tileCount×E`，按节点/边分工则取决于每核边数和重复入度。
3. 分别计算核权成本：`B×K` 的全核常驻与 `E×S` 的按边局部加载，不能只优化其中一个而忽略另一个。
4. 把核数当作每个骨架自己的自变量重新扫描。旧骨架的“8 核最好”不能否决新骨架的 48 核。
5. 保留通用回退，并为每条分派记录语义条件、容量条件、性能条件和负对照。

## What To Verify

- 沿 host 日志或静态分派表确认每个测试点实际进入哪条路径。
- 重边、同一目标多入边、孤立节点、自环、可选输入、转置布局和非对齐形状。
- 所有路径共享同一数学参考；至少覆盖 `mean/add`、fp32/bf16、开闭样条和 `K>S`。
- 每条路径独立测核数，不继承旧骨架的排名。

## Evidence

我们的 host 将并行度限制为 `clamp(ceil(N/16),8,16)`，再用约 4 倍核数的 dst tile。公开对照的 host 从 `min(AIV核数,N)` 出发，再按 regime 改写核数与 `SINGLE/SPARSE` key。

中档不是“所有指标都更少”：其 48 核全量核权总流量高于我们的 8 核版本，但每核节点和边扫描更少，并行度更高。这正说明性能要按最慢执行核和完整流水总账判断，不能挑选单一字节指标解释全部结果。

## Failure Bounds

公开对照包含若干很具体的形状与尾块条件。这些条件证明其实现工程覆盖很细，不证明这些常量适合隐藏用例。复用时应提取 regime 和成本公式，而不是照抄公开 `N` 的特判。

## Related Cards

- [稀疏图按命中边取局部核权](sparse_graph_local_weight_fetch.md)
- [按目标节点重组 SplineConv 聚合](splineconv_group_by_destination.md)
- [把 shape 特化维护成可生成、可审计的配置](manageable_shape_specialization.md)
- [负结果只关闭变体](negative_result_closes_variant_only.md)
