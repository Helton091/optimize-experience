---
type: "Optimization"
title: "归约慢时重构整条延迟链"
description: "当归约由 GM、屏障和标量往返共同构成时，单项成本不一定可加；应按依赖图减少中间态和回读。"
tags: ["task.optimization", "topic.reduction", "topic.latency_chain"]
status: "stable"
sources: [{"resource":"https://atomgit.com/cann/elec-ops-inspection/blob/105feff73c578196614319d1dc5392c147577cb1/2026_elec_operator_competition/final/submissioins/gcw_OTnEiQgj/code/fuseddisconnectorkeypointsoftargmax/op_kernel/kpt_p4.h","role":"implementation"},{"resource":"https://atomgit.com/weixin_43913235/elec-ops-inspection/blob/abd645413c3ef3eb1d70582fb040d2db50abc422/2026_elec_operator_competition/final/submissioins/Helton/code/FusedDisconnectorKeypointSoftArgmax/op_kernel/fdk_vector_body.h","role":"implementation"}]
created_at: "2026-11-17T00:00:00Z"
updated_at: "2026-11-17T00:00:00Z"
platforms: ["ascend910b"]
cann_versions: ["9.0.0"]
aliases: ["EXP-REDUCE-01"]
---
# 归约慢时重构整条延迟链

## Summary

归约不一定受向量算术限制。GM 往返、PipeBarrier、标量回读和通用归约调用可形成串行依赖链；单独删除一个操作时，其他等待可能掩盖收益。

## Use When

- 多项“删掉某操作”的探针收益之和明显小于函数体成本。
- 每 block 向量工作很少，却有多次 GM 或标量往返。
- 通用整图归约调用数量多，但 profiling 无法解释总时间。

## Avoid When

- 尚未确认正确写宽度、mask 和尾块语义。
- 用单项探针的删除量直接宣称完整实现可获得同幅收益。

## Signals

一个历史实现中，单项探针的可见节省合计小于函数体总成本；其结构包含多次 GM 往返、多个全流水屏障和标量读写。该观察表明成本不可简单相加，但不给出另一实现的自动收益。

另一份公开代码使用 `vcmax/vcgmax/vcadd`、行列折叠、预生成坐标与索引映射，并减少最终标量读取。这是可复用的结构线索，不是独立计时分解。

## Method

1. 将归约画成依赖图，标出 V/S/MTE/GM 和同步节点。
2. 合并相互依赖的阶段，减少中间量、标量回读和重复整图扫描。
3. 评估行列两级归约和索引预生成是否减少通用原语开销。
4. 用完整实现验证收益；单项禁用探针只用于定价上限。
5. 对低层 intrinsic 明确写粒度，防止单元素逻辑操作覆盖相邻槽位。

## What To Verify

- max、mass、x/y 矩的数学关系与合并顺序正确。
- 尾块、非整除宽度和标量尾部均有独立测试。
- 向量指令即使逻辑 count 很小，也不会越界覆盖邻近状态。

## Evidence

本卡结合本地历史探针与固定版本公开代码。前者证明“单项成本不一定可加”，后者证明存在另一种归约组织；两者不构成定量因果分解。

## Failure Bounds

若归约已达到真实带宽上限，重写计算链可能没有收益。需先确认瓶颈所属路径。

## Related Cards

- [跨核归约先减少载荷与同步](cross_core_reduction_payload_and_sync.md)
- [先写成本预算再写 kernel](write_cost_budget_before_kernel.md)
