---
type: "Runbook"
title: "经验卡的生命周期与复核"
description: "通过稳定 Concept ID、独立来源、真实复核事件和替代关系维护经验，防止旧结论在后续项目中被误用。"
tags: ["task.validation", "topic.knowledge_governance", "topic.evidence"]
status: "stable"
sources: []
created_at: "2026-11-17T00:00:00Z"
updated_at: "2026-11-17T00:00:00Z"
platforms: ["agnostic"]
aliases: ["EXP-GOVERN-01"]
---
# 经验卡的生命周期与复核

## 适用场景

- 新增、更新、合并、拆分或废弃经验卡。
- 新正式结果、反例、平台或实现使旧结论需要重审。
- 项目删除原始材料后，仍需独立使用经验知识包。

## 触发信号

- 卡片依赖父目录或只有项目内相对链接。
- `stable` 被误当作人工复核，或来源被误当作收益证明。
- 旧卡被直接覆盖，无法知道结论何时以及为何改变。

## 处置步骤

1. 先检索同主题，选择 create、update、merge、split、deprecate 或 defer。
2. 分离原始实验、稳定经验和反例修正；不让日志承担规则定义。
3. 卡片内联关键机制、观测和验证结果，来源使用固定公开版本或工作项。
4. 没有真实复核事件时不写 `verified`；来源不足时保持 `draft`。
5. 废弃卡使用 `replaced_by` 指向现有替代 Concept，并同步所有内部链接。
6. 更新逐层索引、检索用例和当天日志，再运行结构与召回检查。

## 验证信号

- 删除原项目后，卡片正文、导航和检索仍可使用。
- 所有本地正文链接都在本知识包内，公开 Git 来源固定到 40 位 commit。
- 新卡至少有一个真实查询能召回，且不会出现在明确冲突的平台过滤中。
- 环境或 CI 故障没有被写成硬件、API 或 kernel 缺陷。

## 失效边界

结构检查和检索命中都不能证明技术结论正确。高风险结论仍需回到源码、实验或正式结果。

## 相关卡片

- [负结果只关闭变体](../../optimizations/negative_result_closes_variant_only.md)
- [把 shape 特化维护成可审计配置](../../optimizations/manageable_shape_specialization.md)
