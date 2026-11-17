---
type: "Optimization"
title: "用最终输出误差预算决定数值路径"
description: "降精度前应写误差到最终输出的传播式；中间量误差、不同输出误差和不同补偿算法不能混为同一结论。"
tags: ["task.optimization", "topic.precision", "topic.data_type"]
status: "draft"
sources: [{"resource":"https://atomgit.com/cann/elec-ops-inspection/blob/105feff73c578196614319d1dc5392c147577cb1/2026_elec_operator_competition/final/submissioins/gcw_OTnEiQgj/code/fuseddisconnectorkeypointsoftargmax/op_kernel/fused_disconnector_keypoint_soft_argmax.cpp","role":"constraint"}]
created_at: "2026-11-17T00:00:00Z"
updated_at: "2026-11-17T00:00:00Z"
platforms: ["ascend910b"]
cann_versions: ["9.0.0"]
aliases: ["EXP-NUMERIC-01"]
---
# 用最终输出误差预算决定数值路径

## Summary

是否降精度取决于最终输出的误差，而不是某个中间张量的相对误差。坐标期望、最大值分数和其他输出可能具有完全不同的敏感度。

## Use When

- 需要评估 FP16、BF16、HF32 或补偿乘法。
- 中间量误差很小，但尚不清楚传播到输出的影响。
- 不同输出可以拆分数值路径。

## Avoid When

- 用中间量相对误差直接与输出容差比较。
- 把一种补偿算法的失败推广为整个 dtype 不可用。
- 把公开 FP32 对照实现误读成已采用降精度。

## Signals

- 对坐标期望，扰动可写为 `Δkp ≈ Σ p_i (x_i - μ) δ_i`，需要结合概率集中程度和坐标范围评估。
- 对最大值分数，输出直接保留量化台阶，大绝对值处可用容差可能远小于该台阶。
- 历史私有参考实验曾出现 HF32 未通过、补偿 FP16 通过其冻结测试的相反结果；这些原始数据未公开，因此本卡保持 `draft`。

## Method

1. 为每个输出写误差传播式，并计算实际容差 `atol + rtol × |expected|`。
2. 记录 `maxAbsError` 与 `error/tolerance`，不只写“结果相近”。
3. 区分输入舍入、累加、指数、归约和最终舍入的来源。
4. 必要时让坐标与分数使用不同精度路径，或对敏感输出保留 FP32。
5. 用独立参考实现覆盖平坦、尖峰、大 logits、负峰值和特殊值。

## What To Verify

- 所有输出逐元素满足容差，并保留最大误差及容差比。
- 比较相同输入分布和相同数学语义。
- 任何补偿算法都单独测量其计算和搬运成本。

## Evidence

公开固定版本对照代码使用 FP32，证明在降精度前仍有结构优化空间。私有历史数值结果只作为待复核线索，不作为公开实测结论。

## Failure Bounds

本卡尚未提供可公开复核的完整精度数据。平台、输入分布和数学路径变化后必须重新计算预算。

## Related Cards

- [AIV、Cube 与 MIX 按端到端总账选择](evaluate_compute_unit_end_to_end.md)
- [负结果只关闭变体](negative_result_closes_variant_only.md)
