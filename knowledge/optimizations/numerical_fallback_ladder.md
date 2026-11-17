---
type: "Optimization"
title: "给快速数值路径设计分级回退，而非只写成功分支"
description: "快速消元、激活和几何路径应以廉价检查识别异常，再按残差修正、部分主元、高精度或稳健算法逐级回退，并记录各级触发条件。"
tags: ["task.optimization", "topic.precision", "topic.fast_path", "topic.evidence"]
status: "stable"
sources: [{"resource":"https://gitcode.com/cann/elec-ops-inspection/blob/248cf09e66164d0567339ebc79c3c9acf792f962/2026_elec_operator_competition/preliminary/submissioins/zju_liantian/code/det/op_kernel/linalg_det.cpp","role":"implementation"},{"resource":"https://gitcode.com/cann/elec-ops-inspection/blob/248cf09e66164d0567339ebc79c3c9acf792f962/2026_elec_operator_competition/preliminary/submissioins/xjtu_delicate02/code/firecandidatedecodefusion/op_kernel/fire_small_decode.h","role":"implementation"},{"resource":"https://gitcode.com/cann/elec-ops-inspection/blob/248cf09e66164d0567339ebc79c3c9acf792f962/2026_elec_operator_competition/preliminary/submissioins/xjtu_qingmengyaxinghe/code/treelinemindistance/op_kernel/tree_line_min_distance.cpp","role":"implementation"}]
created_at: "2026-11-17T12:13:43Z"
updated_at: "2026-11-17T12:13:43Z"
platforms: ["ascend910b"]
cann_versions: ["9.0.0"]
aliases: ["EXP-NUMERIC-LADDER-01"]
---
# 给快速数值路径设计分级回退，而非只写成功分支

## Summary

多份高分实现并没有把快速数值路径当成“通常都能算对”的赌注，而是同时实现检查、修复和稳健算法。可复用的组织方式是一个降级阶梯：快速路径 → 廉价异常检查 → 残差修正或局部修复 → 更稳健的完整算法。

检查什么、回退到哪一级取决于数学失败模式，不能用单一的 `isfinite` 代替全部数值论证。

## Use When

- 消元、主元、逆迭代、激活或几何比较可能遇到非有限值、强相消、上溢、零分母或平局。
- 快速路径与稳健路径的成本差距足以覆盖检查和偶发回退。
- 公开测试无法覆盖所有病态输入，但接口仍要求完整语义。

## Avoid When

- 检查条件与真实失败原因无关，或用 shape 代替数值检查。
- 回退路径只是注释或死代码，没有独立正确性验证。
- 为了省略补偿而求助于未经验证的近似公式、FMA 合并或重结合。

## Signals

固定版本代码给出了三类不同回退：

- Det：非主元快速消元遇到异常结果时，可在同次 NPU 调用中进入部分主元重算；代码还区分“零主元”和“矩阵奇异”。
- FireCandidateDecodeFusion：小路径检查 Sigmoid 上溢风险，`needsRepair` 时进入独立修复实现，然后继续解码输出。
- TreeLine：对宽坐标行和共线平局设置精确修正/证书路径，避免仅凭一次浮点比较接受平局。

这些例子证明“回退”不是笼统的异常处理，而是针对具体数值失败模式设计。

## Method

把路径拆成明确的级别，而不是一个模糊的 `fallback`：

1. **L0 快速路径**：保留最快且已验证的主实现。
2. **L1 廉价检查**：检查真实主元、残差、非有限值、上溢范围、零范数或候选平局。
3. **L2 局部修复**：残差迭代精化、局部重算或针对性补偿，避免无条件重做全部工作。
4. **L3 稳健完整路径**：部分主元、Householder/QR、Jacobi SVD、精确有理数或其他经过验证的实现。
5. 为每一级记录触发条件、输出语义、最大额外成本和下一级入口。

## What To Verify

- 零主元、奇异矩阵、强相消、零范数、非有限值、上溢/下溢、重复特征值和几何平局。
- 每级回退都能被独立负对照触发，不能只证明主路径通过。
- L2 与 L3 的数值结果满足同一输出容差，并保留触发次数和性能数据。
- 多核重算不发生重复写、工作区污染或同步遗漏。

## Evidence

本卡引用的是固定版本公开代码事实。公开排名不能证明每一级回退都被公开用例触发，也不能证明增加回退没有成本。采用时应分别测量主路径与病态路径。

## Failure Bounds

本卡不保证某一级别对所有算子必要。若快速路径本身已满足完整数值范围，新增级别只会增加成本；若输入语义允许近似，也必须先把允许误差写入接口与测试。

## Related Cards

- [特殊输入快路径必须检查真实值并保留回退](device_checked_fast_path.md)
- [用最终输出误差预算决定数值路径](output_error_budget.md)
- [负结果只关闭变体，不自动关闭方向](negative_result_closes_variant_only.md)
- [先做有效工作量选择，再决定向量化方式](selective_work_before_vectorization.md)
