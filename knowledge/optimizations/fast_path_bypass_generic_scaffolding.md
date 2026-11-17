---
type: "Optimization"
title: "热路径绕过整套通用脚手架，而不只减少几个字段"
description: "微小 workload 的专用入口可绕过完整 tiling 物化、通用类初始化、TPipe/arena 和无效核权预载；旧空核地板不能直接当作新入口下限。"
tags: ["task.optimization", "topic.latency_chain", "topic.specialization", "topic.tiling"]
status: "stable"
sources: [{"resource":"https://gitcode.com/Zhanng-Whu/elec-ops-inspection/blob/f36ce9522ea84a30c5ce6e71ee7a473d53efff09/2026_elec_operator_competition/preliminary/submissioins/whu_Zhanng-Whu/code/splineconv/op_kernel/spline_conv_single.h","role":"implementation"},{"resource":"https://gitcode.com/Zhanng-Whu/elec-ops-inspection/blob/f36ce9522ea84a30c5ce6e71ee7a473d53efff09/2026_elec_operator_competition/preliminary/submissioins/whu_Zhanng-Whu/code/splineconv/op_kernel/spline_conv_single_bulk_stage.h","role":"implementation"},{"resource":"https://github.com/Helton091/SpineConv/blob/984fce058894b6f3f9cf23b6a12d7e9d65925558/splineconv_template/op_kernel/spline_conv.cpp","role":"implementation"}]
created_at: "2026-11-17T11:29:26Z"
updated_at: "2026-11-17T11:29:26Z"
platforms: ["ascend910b"]
cann_versions: ["9.0.0"]
aliases: ["EXP-SPLINE-ENTRY-01"]
---
# 热路径绕过整套通用脚手架，而不只减少几个字段

## Summary

我们的优化曾从整结构 tiling 读取改成按需读字段、把多个 TBuf 合并成一个 arena，再移除 TQue；这些改动保留了同一个通用类初始化和执行骨架。公开单边快路径则直接绕开这套骨架，说明“通用入口里省一点”与“热路径根本不进入通用入口”是两种不同量级的改写。

## Use When

- `E=1` 或其他极小 workload 的通用元数据、队列和预取已接近实际计算成本。
- 专用路径能用编译期常量、`GetBlockNum/GetBlockIdx` 或极少字段确定执行计划。
- 很多核没有实际命中，却仍执行相同的元数据、核权预载和收尾。

## Avoid When

- 为省初始化而使用未初始化 tiling 字段、未配对 event 或未检查对齐。
- 只复制专用入口，却没有保留通用回退与边界测试。
- 把旧探针在另一 kernel、另一调度模式下的空核时间当成不可突破的平台常数。

## Signals

固定版本的公开单边路径展示了以下代码事实：

- `SINGLE` 模板分支在通用 `GET_TILING_DATA_WITH_STRUCT` 之前返回。
- `Raw && One` 可从 `GetBlockNum()` 恢复节点数，从编译期 `Closed0/Closed1` 恢复缩放，不物化完整 tiling。
- 部分 staged 实现直接用 `LocalTensor(TPosition::VECCALC, offset, size)` 指定 UB，而不是建立通用 `TPipe/TBuf` 体系。
- `RunSingleStatic` 只有 `owns` 的执行核才搬入核权；我们的 `ProcessDense()` 则对所有执行核预载全核。

我们的 `ReadTilingFields()` 在典型 `dim=2` 下仍读取约 13 个标量字段，并执行通用 `InitMeta`、GM 绑定、arena 和 per-tile 状态初始化。少读字段与完全不读不是同一个优化层级。

## Method

1. 先写热路径真正需要的最小事实集：shape、图、核权、输出、同步和对齐。
2. 能用编译期 key 或分工恢复的事实，不再从 GM tiling 重读；必须保留的字段按需读取。
3. 让没有命中边的核尽早退出或只承担清零，不为它们预载不会消费的核权。
4. 静态 UB 布局必须带容量、重叠和 32B 对齐检查；eventID 仍须成对。
5. 以完整入口 A/B 比较，不把旧空核探针的时间直接扣除后宣称收益。

## What To Verify

- 快路径未读取任何未初始化字段，host 与 device 对核数、尾块和闭样条缩放的推导一致。
- 无命中、命中首个/末个节点、非对齐输出、异常索引和单核/多核情况。
- 提前返回路径没有遗留 flag、workspace 或未写输出。
- 对照空核与真实实现的构建、调度模式和计时窗口相同。

## Evidence

公开代码证明存在绕过完整通用入口的实现方式；我们的历史空核数字只描述当时的生产骨架。两者之间可以做机制假设，但不能把对照成绩减去旧空核数字，直接声称某项初始化的独立收益。

公开实现还在部分小档使用 `SetScheduleMode(1)`。这是一个应单独 A/B 的调度变量，不能仅凭代码存在就把提速归因于它。

## Failure Bounds

静态特化越多，隐藏形状、新布局和可选输入越容易走错路径。任何“无需 tiling”的结论都只能限于能由其他事实完整恢复执行计划的实例。

## Related Cards

- [按图 regime 选择执行骨架](sparse_graph_regime_dispatch.md)
- [归约慢时重构整条延迟链](restructure_reduction_latency_chain.md)
- [把 shape 特化维护成可生成、可审计的配置](manageable_shape_specialization.md)
