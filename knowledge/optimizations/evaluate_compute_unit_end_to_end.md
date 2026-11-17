---
type: "Optimization"
title: "AIV、Cube 与 MIX 按端到端总账选择"
description: "计算单元选择必须包含布局转换、GM 交接、同步、发射和核心切换；局部 kernel 胜负或理论峰值不能单独决定路线。"
tags: ["task.optimization", "topic.compute_unit", "topic.end_to_end"]
status: "stable"
sources: [{"resource":"https://atomgit.com/cann/elec-ops-inspection/blob/105feff73c578196614319d1dc5392c147577cb1/2026_elec_operator_competition/final/submissioins/gcw_OTnEiQgj/code/fuseddisconnectorkeypointsoftargmax/op_kernel/fused_disconnector_keypoint_soft_argmax.cpp","role":"implementation"},{"resource":"https://cannjudge.cn/submission/6af956ed6bd0f9be37c2a42f","role":"evidence"},{"resource":"https://cannjudge.cn/submission/6af9635e6bd0f9be37df08c6","role":"evidence"}]
created_at: "2026-11-17T00:00:00Z"
updated_at: "2026-11-17T00:00:00Z"
platforms: ["ascend910b"]
cann_versions: ["9.0.0"]
aliases: ["EXP-UNIT-01"]
---
# AIV、Cube 与 MIX 按端到端总账选择

## Summary

不要因 AIV 指令模型出现地板就断言必须换 Cube，也不要因 Cube 局部更快就忽略核心切换。路线选择必须比较完整调用总账。

## Use When

- AIV 指令或 UB 流量接近当前结构上限。
- Cube 设备侧明显更快，但端到端收益不确定。
- 考虑 MIX、融合、跨 stream 或减少 kernel 发射。

## Avoid When

- 只比较 `Axpy` 与 `Mmad` 的理论计算时间。
- 把某个未优化或错误原型当成计算单元的最终判定。
- 把一次设备侧最小值当成正式端到端结论。

## Signals

一个公开对照实现的固定版本主路径使用 FP32 AIV，并在同一任务的正式公开点上快于另一 FP32 AIV 实现约 1.92×（八点合计）。这直接证明“所有 AIV 结构都已到顶”的说法不成立。

另一组历史本地实验曾观察到：

- Cube quad 降低部分 conv 的设备时间；
- b=1 时核心类型切换抵消局部收益；
- 某些 MIX、跨 stream 和 stride 变体正确但更慢。

这些观察只约束各自实现，不构成“Cube 无用”或“融合无用”的通用结论。

## Method

比较以下总成本，而不是只比较计算核心：

```text
计算 + 布局转换 + GM 交接 + 同步 + 发射 + 核心切换 + workspace 准备 + 调用封装
```

1. 先分别测量设备侧与端到端，确定差距发生在哪一层。
2. 保持数学语义、精度和输入输出一致。
3. 对每种路线使用其合理优化后的版本，不以弱原型代表路线。
4. 用目标正式封装做最终采用判断。

## What To Verify

- 核心切换和 workspace 准备没有被排除在计时窗口外。
- 各路线都有完整正确性和回退路径。
- 设备侧收益与端到端方向不一致时，以目标口径为准。

## Evidence

公开代码和正式回执证明 FP32 AIV 反例。其他本地观察仅作为设计警示，不公开宣称未复核的精确收益比例。

## Failure Bounds

本卡不决定 Cube 或 AIV 谁更优，只规定比较方法。设备、形状、封装或实现变化都可能改变选择。

## Related Cards

- [先写成本预算再写 kernel](write_cost_budget_before_kernel.md)
- [负结果只关闭变体](negative_result_closes_variant_only.md)
- [分离比较、归因与正式采用](../runbooks/performance/separate_comparison_attribution_adoption.md)
