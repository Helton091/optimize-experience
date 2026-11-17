---
type: "Runbook"
title: "分离性能比较、设备归因与正式采用"
description: "当本地波动、设备 profile 和正式回执方向不一致时，按三层证据分别判断，不用单一口径承担所有结论。"
tags: ["task.performance_analysis", "topic.measurement", "topic.profiling"]
status: "stable"
sources: [{"resource":"https://cannjudge.cn/submission/6af9635e6bd0f9be37df08c6","role":"evidence"}]
created_at: "2026-11-17T00:00:00Z"
updated_at: "2026-11-17T00:00:00Z"
platforms: ["ascend910b"]
aliases: ["EXP-MEASURE-01"]
---
# 分离性能比较、设备归因与正式采用

## 适用场景

- 共享设备上的微秒级 kernel 测量波动明显。
- 设备 profile 显示收益，但端到端没有同幅改善。
- 本地代理与正式回执的方向或数值不一致。

## 触发信号

- 同一份代码跨轮测量出现不可忽略差异。
- 用两次端到端累计差推算某个 kernel，却没有设备侧证据。
- 设备 kernel 更快，但调用封装、核心切换或 workspace 准备变慢。

## 处置步骤

1. **比较**：在同一 session、同一构建和同一用例下交替运行 A/B，保留预热、样本数、原始样本和统计口径。
2. **归因**：用设备 profile 或真实结构探针确认目标 kernel/阶段，不用低噪声要求之外的端到端差分替代。
3. **采用**：通过目标正式封装运行，记录 workspace、同步、核心切换和外部成本，最终以正式结果决定。
4. 先实测当前设备的噪声底，不把其他项目的固定百分比阈值直接沿用。
5. 报告设备收益与端到端收益两列；方向不一致时分别下结论。

## 验证信号

历史测量中曾出现两类相反问题：

- 端到端差分误判 conv 没有收益，改用设备 profile 后才确认真实下降。
- Cube 的设备 kernel 合计更快，但核心类型切换使端到端多轮稳定更慢。

这些事件证明三层证据不能互换，不提供可移植的固定噪声阈值。

## 失效边界

单次最小值、单次中位数或聚合合计都不能覆盖逐点回退。设备空闲程度、样本分布和统计目标变化时，需要重新选择口径。

## 相关卡片

- [用逐点差距选择结构优化目标](../../optimizations/target_driven_optimization.md)
- [AIV、Cube 与 MIX 按端到端总账选择](../../optimizations/evaluate_compute_unit_end_to_end.md)
