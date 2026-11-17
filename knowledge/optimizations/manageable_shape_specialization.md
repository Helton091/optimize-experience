---
type: "Optimization"
title: "把 shape 特化维护成可生成、可审计的配置"
description: "编译期特化可消除热路径分支，但应集中管理行带、缓冲、同步和容量约束，避免复制 kernel 与魔术偏移失控。"
tags: ["task.optimization", "topic.specialization", "topic.maintainability"]
status: "stable"
sources: [{"resource":"https://atomgit.com/cann/elec-ops-inspection/blob/105feff73c578196614319d1dc5392c147577cb1/2026_elec_operator_competition/final/submissioins/gcw_OTnEiQgj/code/fuseddisconnectorkeypointsoftargmax/op_kernel/kpt_p1.h","role":"implementation"},{"resource":"https://atomgit.com/weixin_43913235/elec-ops-inspection/blob/abd645413c3ef3eb1d70582fb040d2db50abc422/2026_elec_operator_competition/final/submissioins/Helton/code/FusedDisconnectorKeypointSoftArgmax/op_kernel/launch_plan.h","role":"implementation"}]
created_at: "2026-11-17T00:00:00Z"
updated_at: "2026-11-17T00:00:00Z"
platforms: ["agnostic"]
aliases: ["EXP-SPECIALIZE-01"]
---
# 把 shape 特化维护成可生成、可审计的配置

## Summary

特化应服务于明确的热路径收益，而不是堆积不可审查的副本。Host 配置、Device 模板、容量断言和验证映射应由同一份声明式事实生成或核对。

## Use When

- 固定 shape 能消除运行期分支、通用边界或容量计算。
- 多个模式仅在行带、tile、槽数或同步方案上不同。
- 特化数量增加后，修改一个约束需要编辑多处。

## Avoid When

- 尚未证明特化相对通用路径有收益。
- 为单个样例复制完整实现，导致后续 bug 修复无法同步。

## Signals

公开对照代码使用 `SHAPE_MODE`、`GridTrait` 和 `ModeSpec` 固化行数、UB 偏移、槽数和同步选择；另一实现把更多计划集中在运行期 Host 公式中。两者展示了编译期确定性与配置复杂度之间的实际取舍。

## Method

1. 用声明式配置描述 shape、行带、tile、缓冲容量、同步和回退。
2. 用模板或生成器产生特化，避免手工维护多份数学逻辑。
3. 用 `static_assert` 检查 UB 容量、对齐、整除/尾块和事件数量。
4. 保留通用回退，并记录每个模式的测试与采用状态。
5. 将配置名、源码版本和性能结果绑定，避免无身份的“最快配置”。

## What To Verify

- 每个特化均映射到独立 oracle 和边界用例。
- 修改共享规则时所有受影响模式被重新检查。
- 新增编译变体不会引入不可接受的构建或维护成本。
- 通用回退不受特化条件误判影响。

## Evidence

两个固定版本公开实现证明存在不同的特化组织方式。本卡不宣称其中一种在所有项目更优，也不把代码复杂度直接量化为性能收益。

## Failure Bounds

如果配置没有实际消费者或验证需求，不应新增字段和代码生成层。先满足真实模式，再抽象。

## Related Cards

- [按实际成本做非对称分带](cost_based_asymmetric_partition.md)
- [经验卡的生命周期与复核](../runbooks/validations/experience_card_review.md)
