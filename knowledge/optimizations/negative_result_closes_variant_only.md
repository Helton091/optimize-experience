---
type: "Optimization"
title: "负结果只关闭变体，不自动关闭方向"
description: "每个边界结论必须带适用范围、推翻条件和证据，避免把一种布局或封装中的失败误写成平台定律。"
tags: ["task.optimization", "topic.evidence", "topic.negative_result"]
status: "stable"
sources: [{"resource":"https://atomgit.com/cann/elec-ops-inspection/blob/105feff73c578196614319d1dc5392c147577cb1/2026_elec_operator_competition/final/submissioins/gcw_OTnEiQgj/code/fuseddisconnectorkeypointsoftargmax/op_kernel/fused_disconnector_keypoint_soft_argmax.cpp","role":"implementation"},{"resource":"https://atomgit.com/cann/elec-ops-inspection/pull/140","role":"evidence"}]
created_at: "2026-11-17T00:00:00Z"
updated_at: "2026-11-17T00:00:00Z"
platforms: ["agnostic"]
aliases: ["EXP-SCOPE-01"]
---
# 负结果只关闭变体，不自动关闭方向

## Summary

单次实验能直接否定的是当前源码、当前形状和当前封装下的变体。只有给出机制、适用范围和反例条件，才能把结论提升为方向边界。

## Use When

- 准备写“不可行”“到顶”“平台不支持”或“方向关闭”。
- 新证据与已有经验冲突。

## Avoid When

- 尚未阅读实际实现或原始结果。
- 仅因一个未优化原型失败就评价整个计算单元或 API。

## Signals

本知识包来源项目曾出现以下需要缩小范围的判断：

| 旧判断 | 反例或修正 |
|---|---|
| 非零 workspace 必然附带固定大预留 | 问题来自特定取址和封装组合；正确系统基址与小 workspace 可以工作 |
| 32 B 对齐决定水平移位必须复制多份平面 | 更换 packed 布局或延后移位后，成本结构改变 |
| 边界写某个变体更慢，所以边界优化关闭 | 只否定了对应 mask、DMA 和布局组合 |
| AIV 已到通用下限，只能换 Cube 或降精度 | 公开对照实现使用 FP32 AIV，仍在同一任务上显著更快 |
| 减少 kernel 数一定更快 | 若干 MIX/融合变体正确但更慢，但不构成对所有融合的否定 |

## Method

1. 将结论写成四列：主张、适用范围、推翻条件、证据。
2. 主动寻找一个通过的反例，尤其检查布局、取址、dtype、同步 key 和封装变化。
3. 找不到反例时写“当前证据未覆盖”，不要写“平台不支持”。
4. 新反例出现时保留旧记录，并明确替代或缩小旧结论。
5. 区分“有收益的变体尚未实现”和“已经实现且稳定更慢”。

## What To Verify

- 反例的源码、平台、精度、形状和计时口径与主张相关。
- 修正历史文档时保留原始时间线，不掩盖旧错误。
- 每个关闭结论都能被一句具体的反例条件推翻。

## Evidence

固定版本公开代码包含 FP32 AIV 路径，直接反驳“该任务必须换单元或 dtype”的泛化说法。其他修正只覆盖各自实现，不自动证明新的方案一定更快。

## Failure Bounds

本卡约束推理和记录方式，不评价某个具体技术方向的真实收益。

## Related Cards

- [先写成本预算再写 kernel](write_cost_budget_before_kernel.md)
- [AIV、Cube 与 MIX 按端到端总账选择](evaluate_compute_unit_end_to_end.md)
- [经验卡的生命周期与复核](../runbooks/validations/experience_card_review.md)
