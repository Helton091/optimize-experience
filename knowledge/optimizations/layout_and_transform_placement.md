---
type: "Optimization"
title: "先改布局和变换位置，再做指令微调"
description: "当多个输入共享后续移位或边界变换时，评估先约减再变换，消除重复数据路径和无效拷贝。"
tags: ["task.optimization", "topic.data_layout", "topic.data_movement"]
status: "stable"
sources: [{"resource":"https://atomgit.com/weixin_43913235/elec-ops-inspection/blob/abd645413c3ef3eb1d70582fb040d2db50abc422/2026_elec_operator_competition/final/submissioins/Helton/code/FusedDisconnectorKeypointSoftArgmax/op_kernel/fdk_vector_body.h","role":"implementation"},{"resource":"https://atomgit.com/cann/elec-ops-inspection/blob/105feff73c578196614319d1dc5392c147577cb1/2026_elec_operator_competition/final/submissioins/gcw_OTnEiQgj/code/fuseddisconnectorkeypointsoftargmax/op_kernel/kpt_p6.h","role":"implementation"},{"resource":"https://cannjudge.cn/submission/6af9495f6bd0f9be37a339cb","role":"evidence"}]
created_at: "2026-11-17T00:00:00Z"
updated_at: "2026-11-17T00:00:00Z"
platforms: ["ascend910b"]
cann_versions: ["9.0.0"]
aliases: ["EXP-LAYOUT-01"]
---
# 先改布局和变换位置，再做指令微调

## Summary

不规则访问的成本往往由数据布局和它发生的阶段决定。若多个输入通道共享同一个水平移位、边界处理或索引变换，应先判断能否在通道约减后只做一次。

## Use When

- 每个输入通道都重复执行相同的 Gather、平移、mask 或补零。
- 为避开对齐限制而复制了多份几乎相同的平面。
- 指令微调只能带来几个百分点，数据路径却存在结构重复。

## Avoid When

- 改写改变数学语义、顺序依赖或输出精度且无法补偿。
- 新布局引入的转换、容量和额外流量已经超过节省项。

## Signals

同一融合算子的演化提供了两个层次：

1. 早期用三份平移拷贝替代逐 tap Gather，但每通道仍有多份拷贝和边界 mask。
2. 后续按水平 tap 分三组累加，在通道累加结束后用两次 Gather 合并。一个正式版本的公开八点合计由 277.910 µs 降到 251.455 µs。

另一份固定版本公开实现也采用“先累加、后平面合并与水平 Gather”的结构。这是代码路径事实，不是其总收益中该项的独立测量份额。

## Method

1. 画出每个输入到输出的完整搬运和变换链。
2. 找出多个输入共享且可与约减交换顺序的变换。
3. 比较“每输入做一次”与“约减后做一次”的字节数、指令数和临时容量。
4. 重新推导对齐、halo、尾块和边界零，不继承旧布局的假设。
5. 保留正确的通用路径，并以同一正式封装比较。

## What To Verify

- 左右边界没有读到相邻行的 wrap 数据。
- 所有向量操作数满足新布局的对齐要求。
- 归约重排的输出误差满足最终容差。
- 新布局的容量和 DMA 成本没有抵消收益。

## Evidence

固定版本的两种实现展示了延后水平变换的具体代码路径；正式回执只用于其中一个已实现版本的整体结果，不能拆出未测模块的独立收益。

## Failure Bounds

本原则不是“Gather 一定慢”或“拷贝一定可删”。结论取决于变换与约减是否可交换以及新物理布局。

## Related Cards

- [DMA 流水与最慢 block](dma_pipeline_and_makespan.md)
- [先写成本预算再写 kernel](write_cost_budget_before_kernel.md)
