# Ascend C 优化经验知识包

这是一个可独立复制、检索和演化的经验知识包。它不读取父目录，不依赖任何算子工程、评测器、私有知识库或外部服务。知识正文位于 `knowledge/`，模板、工具、评测和日志只负责生产、消费与治理。

## 快速使用

- 人读：从 [`knowledge/index.md`](knowledge/index.md) 进入，逐层查看卡片摘要。
- 检索：在本目录运行 `python3 tools/query.py "跨核 归约" --platform ascend910b`。
- 检查：运行 `python3 tools/check.py`，检查卡片、导航、内部链接和检索用例。
- Windows 可将命令中的 `python3` 换成可用的 Python 启动命令；工具仅使用 Python 标准库。

Query 默认只返回 `stable` 卡。候选命中不代表技术结论适用于当前任务，仍需阅读全文、平台、版本、证据和失效边界。

## 目录职责

| 路径 | 职责 |
|---|---|
| `knowledge/optimizations/` | 可复用优化方法：触发条件、收益来源、失效边界和验证方式 |
| `knowledge/runbooks/` | 按性能测量或验证任务组织的处置闭环 |
| `templates/` | 新卡模板，不参与检索 |
| `tools/` | 本地查询与质量检查 |
| `evals/` | 检索回归，不评价技术答案本身 |
| `logs/` | 已实施的知识变更，不是规则事实源或待办清单 |

## 知识模型

每张卡是带 YAML Frontmatter 的 Markdown。为保持零依赖，Frontmatter 的每个值都写成单行 JSON 值；JSON 是 YAML 的合法子集。例如：

```yaml
---
type: "Optimization"
title: "示例优化方法"
description: "不打开正文也能理解的摘要。"
tags: ["task.optimization", "topic.data_movement"]
status: "draft"
sources: []
created_at: "2026-11-17T00:00:00Z"
updated_at: "2026-11-17T00:00:00Z"
platforms: []
aliases: ["EXP-EXAMPLE-01"]
---
```

规则：

- `type`、`title`、`description`、`tags`、`status`、`sources`、`created_at`、`updated_at`、`platforms` 为必选字段。
- `type` 必须与路径一致：`optimizations/` 为 `Optimization`，`runbooks/` 为 `Runbook`。
- `tags` 为 2–6 个不重复标签，至少一个 `task.*` 和一个 `topic.*`。
- `platforms` 使用 `ascend910b` 或 `agnostic`；`draft` 可用空数组表示范围待确认。`agnostic` 不表示平台未知。
- `cann_versions`、`aliases`、`verified`、`replaced_by` 为可选字段。没有真实复核事件时不写 `verified`。
- `status: stable` 表示可在声明范围内消费，不表示经过人工复核；`draft` 表示来源或范围待补；`deprecated` 表示仅为历史引用保留。
- `deprecated` 必须用 `replaced_by` 指向另一个现有 Concept；其他状态不得使用该字段。
- Concept ID 是路径相对 `knowledge/` 并去掉 `.md`，例如 `optimizations/layout_and_transform_placement`。移动卡片会改变 Concept ID，必须同步内部链接与 `replaced_by`。
- 原长文档的 `EXP-*` 编号保存在 `aliases`，用于兼容检索。

## 来源与独立性

- 卡片必须自包含理解结论所需的机制、关键观测和验证结果，不依赖原项目上下文。
- `sources` 只使用可复核的公开 URL。Git 文件或目录来源固定到 40 位 commit；正式 PR、Issue 和评测回执使用其工作项 URL。
- 不使用分支头部作为 Git 证据，不使用本地绝对路径、父目录相对链接、私有仓库、账号、令牌或不可公开数据。
- 本地 trace 型 Runbook 可使用 `sources: []`，但正文必须保留触发、探针、原始观测、验证信号和范围；不得把 Agent 叙述伪装成工具观测。
- `stable` 的 Optimization 至少有一个公开来源。来源不足时保持 `draft` 或暂缓写入，不创建占位卡。
- 正文普通 Markdown 本地链接只能解析到 `knowledge/` 内的现有文件；公开 HTTPS 来源链接不受此限制。
- 环境、网络或 CI 故障只记录为环境事实，不据此推导 kernel 或硬件限制。

## 新增与演化

1. 先检索相同主题，阅读候选卡，再决定 create、update、merge、split、deprecate 或 defer。
2. 从 `templates/` 创建卡片，写清结论、适用条件、失效边界和验证方式。
3. 区分正式实测、本地实测、代码事实、机制推断和反例；单次变体失败不得写成整个方向关闭。
4. 更新所有相关层级的 `index.md`，索引只列直接子项并附摘要。
5. 运行 `python3 tools/check.py`；新增知识还必须有一个能召回它的真实查询用例。
6. 在当天 `logs/YYYY-MM-DD.md` 追加已执行的操作和结果。纯排版修订不记日志。
7. 不自动提交、推送或发布；公开分享前另行完成许可证和隐私审查。

## 当前范围

当前卡片来自 Ascend 910B / CANN 9.0.0 的 FP32 卷积与 Soft-Argmax 融合优化对照，以及一次 SplineConv 稀疏小图公开实现复盘。后者补充了图 regime 分派、局部核权、按目标节点聚合和最小入口等主题。它们提供方法、代码事实和反例，不代表对其他芯片、CANN 版本、DSL、算子或隐藏用例已有覆盖。
