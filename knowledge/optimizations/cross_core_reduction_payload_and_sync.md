---
type: "Optimization"
title: "跨核归约先减少交换载荷与同步"
description: "跨核优化应核算统计量字节、GM 往返和屏障；小 workspace 与输出暂存具有不同契约，输出 scratch 不能默认移植。"
tags: ["task.optimization", "topic.cross_core", "topic.workspace"]
status: "stable"
sources: [{"resource":"https://atomgit.com/weixin_43913235/elec-ops-inspection/blob/abd645413c3ef3eb1d70582fb040d2db50abc422/2026_elec_operator_competition/final/submissioins/Helton/code/FusedDisconnectorKeypointSoftArgmax/op_kernel/fdk_single_entry.h","role":"implementation"},{"resource":"https://atomgit.com/cann/elec-ops-inspection/blob/105feff73c578196614319d1dc5392c147577cb1/2026_elec_operator_competition/final/submissioins/gcw_OTnEiQgj/code/fuseddisconnectorkeypointsoftargmax/op_kernel/kpt_p5.h","role":"implementation"}]
created_at: "2026-11-17T00:00:00Z"
updated_at: "2026-11-17T00:00:00Z"
platforms: ["ascend910b"]
cann_versions: ["9.0.0"]
aliases: ["EXP-MERGE-01"]
---
# 跨核归约先减少交换载荷与同步

## Summary

跨核归约的收益由并行计算减去统计交换、GM 往返、同步和最终写回成本。先减少归约链上的载荷与等待，再决定增加多少分带。

## Use When

- 单图/单任务归约无法填满核心。
- 每个分带已有可结合的部分状态，如 max、mass 和坐标矩。
- workspace、同步或输出写回占据显著成本。

## Avoid When

- 部分状态不能按明确代数合并。
- 所有参与 block 无法同波常驻，却仍使用全局屏障。
- 调用契约不允许输出在最终写回前承载中间态。

## Signals

两种公开实现展示了不同的合并方式：

- 实现 A 为每个分带写 32 B 对齐统计记录，通过系统 workspace 基址交换；全局同步后由 leader 读取并重标定。
- 实现 B 在较少分带时使用 CrossCore Flag 形成短合并链，将统计量编码到少量字，并暂存在输出张量中；更多分带的备用路径还包含 GM atomic 和多次全局同步。

实现 B 的 `PackVec64` 证明可以压缩中间载荷，但其输出暂存、编码精度和最终覆盖语义必须单独审查，不能视为通用 workspace 替代。

## Method

1. 写出部分状态的代数：全局 max 后按 `exp((m_i-M)/tau)` 重标定 mass 和矩。
2. 统计每块记录大小、读写次数、Flag/SyncAll 数量和最终写回次数。
3. 优先选择明确申报的小 workspace，并使用正确的系统基址和同步 key。
4. 若考虑输出暂存，单独验证别名、精度、异常恢复、重复调用和最终覆盖。
5. 用实际 ACLNN/目标封装验证同步，不用直调通过替代正式路径。

## What To Verify

- 所有参与块按同一事件图执行，Set/Wait 数量匹配。
- `SyncAll` 的 grid 不超过一波可常驻数量。
- 多次调用不读取到上次输出或旧 workspace 内容。
- 合并后的数值误差满足最终输出容差。

## Evidence

两种固定版本代码提供直接实现证据。本卡不推荐输出 scratch 作为通用默认，只把它列为高风险特化变体。

## Failure Bounds

workspace 大小、指针和封装是不同变量；任一变化都需要重新验证。直调、ACLNN 和不同 tiling key 的同步能力不能互相推定。

## Related Cards

- [按实际成本做非对称分带](cost_based_asymmetric_partition.md)
- [归约慢时重构整条延迟链](restructure_reduction_latency_chain.md)
