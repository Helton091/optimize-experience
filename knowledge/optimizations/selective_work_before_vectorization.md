---
type: "Optimization"
title: "先做有效工作量选择，再决定向量化方式"
description: "高分实现常先减少必须处理的列、边、候选和核权，再选择 Brcb、Gather 或底层指令；检测与建表成本必须计入净收益。"
tags: ["task.optimization", "topic.performance", "topic.data_movement", "topic.specialization"]
status: "stable"
sources: [{"resource":"https://gitcode.com/cann/elec-ops-inspection/blob/248cf09e66164d0567339ebc79c3c9acf792f962/2026_elec_operator_competition/preliminary/submissioins/JLU_op-wuliuqi/code/safetybeltviolationgeometry/op_kernel/sbg_kernel_common.h","role":"implementation"},{"resource":"https://gitcode.com/Zhanng-Whu/elec-ops-inspection/blob/f36ce9522ea84a30c5ce6e71ee7a473d53efff09/2026_elec_operator_competition/preliminary/submissioins/whu_Zhanng-Whu/code/splineconv/op_kernel/spline_conv_local_weights.h","role":"implementation"},{"resource":"https://gitcode.com/cann/elec-ops-inspection/blob/248cf09e66164d0567339ebc79c3c9acf792f962/2026_elec_operator_competition/preliminary/submissioins/jnu_op-zxfj/code/treelinemindistance/op_kernel/tree_line_spatial.h","role":"implementation"}]
created_at: "2026-11-17T12:13:43Z"
updated_at: "2026-11-17T12:13:43Z"
platforms: ["ascend910b"]
cann_versions: ["9.0.0"]
aliases: ["EXP-SELECTIVE-WORK-01"]
---
# 先做有效工作量选择，再决定向量化方式

## Summary

与其先把全部输入搬进 UB 并寻找更宽的指令，不如先问哪些列、边、候选或矩阵确实参与输出。多份公开高分实现都在向量计算之前设置工作量选择层：只转换必要列、只加载相关核权、只在大规模时建立空间筛选，或在无效任务上提前返回。

这是一层结构优化，不是“少写几条指令”的同义词。检测、建表、额外 DMA 和回退都可能抵消节省。

## Use When

- 输入只有部分字段影响输出，或大量任务/输出为空。
- `E≪N`、`S<K`、候选数很大但有效候选较少。
- 全量预处理、类型转换或全核缓存已占显著成本。

## Avoid When

- 几乎所有输入都有效，筛选本身比直接计算还贵。
- 需要改变数学语义、比较顺序或边界行为才能删除工作。
- 为建立复杂索引而重复扫描的数据量已超过原计算。

## Signals

三个不同算子提供了不同类型的代码证据：

- SafetyBelt 的 FP16 路径只提取并转换 `y1/y2/cy` 三列，而非转换人员框的全部字段；几何计算继续使用 FP32，并保留分步舍入。
- SplineConv 大档按命中边加载 `S=4` 个相关核权矩阵，而不是每个核预载 `K=9` 个全核矩阵。
- TreeLine 只在较大的点线规模下考虑空间排序和保守包围盒筛选；小输入仍走直接标量或点线块路径。

这些事实说明“选择工作”发生在不同层级，不能把它们统一写成某一个 API 的功劳。

## Method

1. 写出输出真正依赖的最小数据集：字段、边、候选、矩阵和节点。
2. 分别计算全量成本与选择后成本：

   ```text
   净收益 = 省去的搬运/转换/计算
            − 条件检查 − 建表/排序 − 新增 DMA/同步 − 回退期望成本
   ```

3. 让选择条件来自真实 shape、属性或数值检查，并为不命中的输入保留完整路径。
4. 只有在节省覆盖建立成本后才使用复杂索引；小输入优先直接路径。
5. 再为剩下的工作选择连续布局、Brcb、Gather、WholeReduce 或底层 intrinsic。

## What To Verify

- 零命中、全命中、重复索引、尾块、非对齐和边界值。
- 被省略字段确实不影响输出，比较次序与舍入没有意外改变。
- 记录选择层自身的扫描、排序、缓存建立和额外回退成本。
- 对未公开 shape 单独验证，不能把公开分布当成全量输入规律。

## Evidence

上述三份固定版本源码形成了“字段选择、核权选择、候选选择”的跨题对照。它们证明这种组织方式确实存在，但没有提供选择层相对全量实现的独立收益分解，因此本卡不给出统一加速比例。

## Failure Bounds

如果数据分布或属性改变使选择层失去过滤能力，应回到全量路径。公开用例中的稀疏性、常数属性和尾块组合不能用于推断隐藏用例。

## Related Cards

- [稀疏图按命中边取局部核权](sparse_graph_local_weight_fetch.md)
- [按图 regime 选择执行骨架](sparse_graph_regime_dispatch.md)
- [先写成本预算再写 kernel](write_cost_budget_before_kernel.md)
- [特殊输入快路径必须检查真实值并保留回退](device_checked_fast_path.md)
