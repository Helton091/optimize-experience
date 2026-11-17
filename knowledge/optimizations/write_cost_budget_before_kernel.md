---
type: "Optimization"
title: "先写成本预算再写 kernel"
description: "用字节、指令、DMA、波数、同步、精度和计算单元构建可证伪预算，避免用“减少开销”代替优化假设。"
tags: ["task.optimization", "topic.performance", "topic.cost_model"]
status: "stable"
sources: [{"resource":"https://atomgit.com/weixin_43913235/elec-ops-inspection/blob/abd645413c3ef3eb1d70582fb040d2db50abc422/2026_elec_operator_competition/final/submissioins/Helton/code/FusedDisconnectorKeypointSoftArgmax/op_kernel/fdk_vector_body.h","role":"implementation"},{"resource":"https://atomgit.com/cann/elec-ops-inspection/blob/105feff73c578196614319d1dc5392c147577cb1/2026_elec_operator_competition/final/submissioins/gcw_OTnEiQgj/code/fuseddisconnectorkeypointsoftargmax/op_kernel/kpt_p7.h","role":"implementation"}]
created_at: "2026-11-17T00:00:00Z"
updated_at: "2026-11-17T00:00:00Z"
platforms: ["ascend910b"]
cann_versions: ["9.0.0"]
aliases: ["EXP-BUDGET-01"]
---
# 先写成本预算再写 kernel

## Summary

优化前先说明候选方案改变了什么可计量成本。模型用于筛选和预测实验，不用于代替测量。

## Use When

- 需要在多种布局、分块、dtype、计算单元或融合方案中排序。
- 一个方案听起来合理，但尚未写出收益上限和新增成本。

## Avoid When

- 成本参数没有来源，或单位、形状、布局没有固定。
- 用局部理论峰值直接预测端到端成绩。

## Signals

至少检查以下轴：

| 轴 | 必须回答的问题 |
|---|---|
| 数据量 | 每 MAC/输出元素搬多少字节？是否存在读放大？ |
| 指令 | 指令数、repeat 数、标量往返各是多少？ |
| DMA | 次数、burst 大小、stride、读写放大是多少？ |
| 调度 | block 数、波数、最慢 block 的工作量是多少？ |
| 同步 | GM 往返、全局屏障、kernel 发射和核心切换各几次？ |
| 数值 | 最终输出的误差预算是多少？哪个输出最敏感？ |

一个历史 AIV 模型曾写成 `T ≈ I × (a + n/b)`：`I` 为每 block 指令数，`n` 为每指令覆盖的元素数。它指导了 KPack 分派，但常数 `a/b` 只属于当时的 FP32 布局和实现，不能继承到其他结构。

## Method

1. 写出基线成本等式，并为常数记录设备、形状、布局和标定样本。
2. 写出候选在同一单位下的新增成本与减少成本。
3. 给出一个能推翻模型的预测，例如某负载应下降多少微秒。
4. 优先实现保留目标成本、但不必完整实现所有业务逻辑的结构探针。
5. 实测后更新模型；若预测失败，记录缺失成本项。

## What To Verify

- 所有流量、指令和时间单位一致。
- 局部探针不被当成业务正确性证据。
- 模型覆盖发射、workspace 准备、同步和封装等外部成本。

## Evidence

两份固定版本实现展示了同一任务的不同指令、DMA 和归约组织方式。卡片中的成本公式是历史标定示例，不是硬件普适常数。

## Failure Bounds

布局、dtype、封装或设备变化时必须重新标定。模型预测不等于采用证据。

## Related Cards

- [用逐点差距选择结构优化目标](target_driven_optimization.md)
- [AIV、Cube 与 MIX 按端到端总账选择](evaluate_compute_unit_end_to_end.md)
