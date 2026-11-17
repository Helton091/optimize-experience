---
type: "Optimization"
title: "特殊输入快路径必须检查真实值并保留回退"
description: "零值或常数输入可用设备检查和解析输出加速，但不能按 shape 假定条件成立；连续单点写回应与通用回退一起验证。"
tags: ["task.optimization", "topic.fast_path", "topic.data_distribution"]
status: "stable"
sources: [{"resource":"https://atomgit.com/weixin_43913235/elec-ops-inspection/blob/abd645413c3ef3eb1d70582fb040d2db50abc422/2026_elec_operator_competition/final/submissioins/Helton/code/FusedDisconnectorKeypointSoftArgmax/op_kernel/fdk_single_entry.h","role":"implementation"},{"resource":"https://atomgit.com/cann/elec-ops-inspection/blob/105feff73c578196614319d1dc5392c147577cb1/2026_elec_operator_competition/final/submissioins/gcw_OTnEiQgj/code/fuseddisconnectorkeypointsoftargmax/op_kernel/kpt_p3.h","role":"implementation"},{"resource":"https://cannjudge.cn/submission/6af956ed6bd0f9be37c2a42f","role":"evidence"}]
created_at: "2026-11-17T00:00:00Z"
updated_at: "2026-11-17T00:00:00Z"
platforms: ["ascend910b"]
cann_versions: ["9.0.0"]
aliases: ["EXP-FASTPATH-01"]
---
# 特殊输入快路径必须检查真实值并保留回退

## Summary

零权重、常数或其他特殊分布可以使用解析输出，但触发条件必须来自设备对真实输入的检查，并提供完整计算回退。shape 只能帮助选择检查策略，不能证明数值条件。

## Use When

- 特殊输入具有明显更便宜的解析结果。
- 多核分别写很小输出导致发射和 DMA 成本突出。
- 检查成本低于完整计算，并且非特殊输入能安全回退。

## Avoid When

- 快路径条件由 shape、样例或测试经验假定，而非实际读取输入。
- 快路径产生的输出与通用路径语义或精度不一致。

## Signals

在一个 B4、48×64 的零权重正式负载中：

- 按 map 检查并分别写输出的实现为 5.733 µs。
- 使用位折叠检查、由 block 0 连续写出整个 batch 的实现为 3.733 µs。

两个公开实现都保留非零权重处理。第二个实现说明“真实检查 + 单点连续写回”值得作为实验方向，但上述差值不是各子项的独立收益分解。

## Method

1. 写出特殊条件的严格数学判定和解析输出。
2. 在设备上读取真实参数；可用位折叠或归约检查是否全零。
3. 非特殊条件立即进入完整计算，不改变输入。
4. 比较小写回与单点连续写回的事务数和发射成本。
5. 让检查与部分参数搬运共享已有工作，避免快路径在普通负载上成本过高。

## What To Verify

- 全零、非零回退、接近零、不同 bias 和不同 batch 均覆盖。
- 快路径与通用路径在相同输入上满足同一输出容差。
- 多核启动时只有指定角色写全量输出，不发生重复或竞争写。

## Evidence

公开结果与两份固定版本实现支持上述结构和总体对照。检查、写回和调度各子项需要另行消融。

## Failure Bounds

特殊分布不在真实负载中出现时，快路径只增加普通路径成本。不得为命中快路径修改输入或测试期望。

## Related Cards

- [用逐点差距选择结构优化目标](target_driven_optimization.md)
- [DMA 流水与最慢 block](dma_pipeline_and_makespan.md)
