---
type: "Optimization"
title: "按实际成本做非对称分带"
description: "空间分带不只平均分配高度，还要计入 halo、尾块、归约角色和同步成本，以最慢带而不是平均工作量做决策。"
tags: ["task.optimization", "topic.tiling", "topic.parallelism"]
status: "stable"
sources: [{"resource":"https://atomgit.com/weixin_43913235/elec-ops-inspection/blob/abd645413c3ef3eb1d70582fb040d2db50abc422/2026_elec_operator_competition/final/submissioins/Helton/code/FusedDisconnectorKeypointSoftArgmax/op_kernel/launch_plan.h","role":"implementation"},{"resource":"https://atomgit.com/cann/elec-ops-inspection/blob/105feff73c578196614319d1dc5392c147577cb1/2026_elec_operator_competition/final/submissioins/gcw_OTnEiQgj/code/fuseddisconnectorkeypointsoftargmax/op_kernel/kpt_p1.h","role":"implementation"},{"resource":"https://cannjudge.cn/submission/6af956ed6bd0f9be37c2a42f","role":"evidence"}]
created_at: "2026-11-17T00:00:00Z"
updated_at: "2026-11-17T00:00:00Z"
platforms: ["ascend910b"]
cann_versions: ["9.0.0"]
aliases: ["EXP-PARTITION-01"]
---
# 按实际成本做非对称分带

## Summary

`parts` 决定并行度，但每带真实成本还包括顶/底 halo、尾块、归约、同步角色和输出责任。平均分行不一定使最慢带最小。

## Use When

- 非归约维产生的任务数不足以填满核心。
- 顶带、中间带和底带具有不同搬运或边界成本。
- 增加分带后部分核心空闲，或同步等待抵消并行收益。

## Avoid When

- 分带偏好的差异尚未通过同形状实验验证。
- 全局屏障所需 block 不能同波常驻。

## Signals

同一任务的两种公开计划存在以下配置差异。每格列出从顶到底的有效行数；它们证明结构不同，不证明行数对总时延的独立贡献。

| B×H×W | 实现 A | 实现 B |
|---|---|---|
| 1×48×64 | 8 / 8 / 8 / 8 / 8 / 8 | 20 / 15 / 13 |
| 1×64×64 | 16 / 16 / 16 / 16 | 26 / 20 / 18 |
| 1×72×96 | 18 / 18 / 18 / 18 | 24 / 16 / 16 / 16 |
| 2×48×64 | 24 / 24 | 20 / 16 / 12 |
| 2×64×64 | 22 / 22 / 20 | 27 / 21 / 16 |
| 4×48×64 | 48 | 27 / 21 |
| 3×72×96 | 24 / 24 / 24 | 36 / 36 |

实现 B 把不同行数和归约顺序编入固定模式；实现 A 主要由统一公式产生行带。

## Method

1. 为每带计算有效行、halo 行、DMA、指令、归约和同步成本。
2. 以 `max(cost_i)` 为目标，而不是只最小化总成本或平均行数。
3. 检查任务映射是否让归约等待集中在某个角色。
4. 把行数作为可检索配置，并以同形状 A/B 决定是否采用。
5. 对不能整除的高度显式处理尾带，不把通用 `Rows` 错用于最后一块。

## What To Verify

- 各带覆盖区间恰好组成完整输入，无重叠或漏行。
- 尾带的 `PadBottom`、输入长度和归约坐标使用实际行数。
- 总 block 数、波数和同步要求满足设备约束。

## Evidence

表中配置可直接从两个固定版本 Host/模式代码复核。没有逐配置的独立性能分解时，只能把它作为下一轮实验假设。

## Failure Bounds

非对称配置是形状和实现相关结果，不应直接复制到其他算子。成本变化后必须重新求解。

## Related Cards

- [跨核归约先减少载荷与同步](cross_core_reduction_payload_and_sync.md)
- [DMA 流水与最慢 block](dma_pipeline_and_makespan.md)
