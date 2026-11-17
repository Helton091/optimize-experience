---
type: "Optimization"
title: "按每槽工作量设计 DMA 流水，并按最慢 block 验收"
description: "DMA 批量、缓冲槽数和 tile 需要联合调节；总吞吐正常仍可能被固定 task 上的少量工作拖长 makespan。"
tags: ["task.optimization", "topic.data_movement", "topic.scheduling"]
status: "stable"
sources: [{"resource":"https://atomgit.com/cann/elec-ops-inspection/blob/105feff73c578196614319d1dc5392c147577cb1/2026_elec_operator_competition/final/submissioins/gcw_OTnEiQgj/code/fuseddisconnectorkeypointsoftargmax/op_kernel/kpt_p7.h","role":"implementation"},{"resource":"https://atomgit.com/weixin_43913235/elec-ops-inspection/blob/abd645413c3ef3eb1d70582fb040d2db50abc422/2026_elec_operator_competition/final/submissioins/Helton/code/FusedDisconnectorKeypointSoftArgmax/op_kernel/fdk_vector_body.h","role":"implementation"}]
created_at: "2026-11-17T00:00:00Z"
updated_at: "2026-11-17T00:00:00Z"
platforms: ["ascend910b"]
cann_versions: ["9.0.0"]
aliases: ["EXP-PIPE-01"]
---
# 按每槽工作量设计 DMA 流水，并按最慢 block 验收

## Summary

双缓冲不是默认最优，增加 block 也不是单调优化。DMA 批量、槽数和 tile 应由搬运与计算的相对成本决定，并以最慢 block 的完成时间验收。

## Use When

- MTE2 发射、窄 burst 或搬运等待占比较高。
- 增加槽数、通道批量或 block 数后性能非单调。
- kernel 中存在只由 `task==0` 等固定块执行的初始化工作。

## Avoid When

- UB 容量、事件 ID 或同步配对尚不明确。
- 只根据平均 block 工作量判断并行效率。

## Signals

- 一次任务中的少量初始化或索引生成挂在固定 block，可能使整个 kernel 等待该块。
- 同一布局在不同形状下可能出现“更多块更快”和“更少块更快”两种结果。
- 一份公开实现按模式选择通道对/小组、两/三槽和不同同步安排；这些不是可脱离形状直接继承的常数。

## Method

1. 列出每槽搬运时间、计算时间和同步时间，选择能覆盖等待的最小槽数。
2. 比较 DMA 合并后的描述符数量、有效字节、stride 和读写放大。
3. 把固定 task 上的一次性工作拆入普通任务网格，或证明它不会成为最慢路径。
4. 按形状扫描 tile 和 block 数，记录每块工作与整段 makespan。
5. 审计所有事件的 Set/Wait 配对和槽位生命周期。

## What To Verify

- 槽数改变后 UB 仍满足容量和对齐约束。
- 多轮重复调用不会发生旧数据污染或事件计数冲突。
- 设备侧改善能兑现到目标封装，而不是被外部成本覆盖。

## Evidence

本知识包来源实验曾观察到：固定 task 的一次性工作使 pack 阶段接近翻倍，拆散后才兑现其他收益；不同形状的 pack tile 也没有统一单调方向。这些是特定实现的本地观测，不是硬件固定比例。

## Failure Bounds

具体槽数、批量和屏障条件只适用于对应形状与实现。不得为追求重叠而省略必要同步。

## Related Cards

- [先写成本预算再写 kernel](write_cost_budget_before_kernel.md)
- [按实际成本做非对称分带](cost_based_asymmetric_partition.md)
