---
type: "Runbook"
title: "10 道题 × 前三名：公开实现与证据边界矩阵"
description: "逐行记录 30 份前三名回执、26 份公开实现、PR 与固定源码链接，以及 4 份未找到源码的缺口；只作证据导航，不作独立性能因果表。"
tags: ["task.performance_analysis", "topic.evidence", "topic.experiment_management"]
status: "stable"
sources: [{"resource":"https://gitcode.com/cann/elec-ops-inspection/tree/248cf09e66164d0567339ebc79c3c9acf792f962/2026_elec_operator_competition/preliminary/submissioins","role":"primary"},{"resource":"https://cannjudge.cn/public/2026_electronic","role":"evidence"}]
created_at: "2026-11-17T12:13:43Z"
updated_at: "2026-11-17T12:13:43Z"
platforms: ["ascend910b"]
cann_versions: ["9.0.0"]
aliases: ["EXP-CROSS-MATRIX-01"]
---
# 10 道题 × 前三名：公开实现与证据边界矩阵

## 使用方式

本表是[第二轮跨题高手习惯总结](cross_problem_expert_patterns.md)的证据附录。每行对应一份当前榜单前三名回执，并给出公开 PR 与固定源码链接；未找到源码的行只保留回执，不做机制归因。

“代码事实”是实际阅读后整理的实现结构，不是性能分解。“证据边界”用于限制结论，尤其注意未命中路径、维护版差异和未独立复测项。

覆盖：**30 份回执；26 份公开实现；4 份未找到公开源码。**

| Problem | Rank | Team / evidence | Code facts | Evidence boundary |
|---|---:|---|---|---|---|
| det | 1 | 炼天魔尊 · [PR#105](https://gitcode.com/cann/elec-ops-inspection/pull/105) · [code](https://gitcode.com/cann/elec-ops-inspection/tree/248cf09e66164d0567339ebc79c3c9acf792f962/2026_elec_operator_competition/preliminary/submissioins/zju_liantian/code/det) | 小矩阵 UB 驻留，大矩阵 team 分块与 AIC/AIV 协同；DetAbnormal/retryAny 进入 PivotedFallback 部分主元重算。 | 回退是代码事实，独立性能收益未分解。 |
| det | 2 | ruby0451 的队伍 · [PR#115](https://gitcode.com/cann/elec-ops-inspection/pull/115) · [code](https://gitcode.com/cann/elec-ops-inspection/tree/248cf09e66164d0567339ebc79c3c9acf792f962/2026_elec_operator_competition/preliminary/submissioins/zju_ruby0451/code/det) | tiny/fullVector/compact/alignedLarge 与通用路径；最大主元、零及 Finite 检查；大路径 AIC/AIV 协同。 | 未见失败后重算回退；当前为维护拆分版，原始获奖版本另有归档，不能混为一谈。 |
| det | 3 | 桀桀桀 · [PR#114](https://gitcode.com/cann/elec-ops-inspection/pull/114) · [code](https://gitcode.com/cann/elec-ops-inspection/tree/248cf09e66164d0567339ebc79c3c9acf792f962/2026_elec_operator_competition/preliminary/submissioins/NCEPU_jiejiejie/code/det) | 小阶静态、通用列分片、n>128 Cube；幅值/小主元检查后 DetRunFallback，采用双浮点补偿与部分主元。 | 补偿与回退边界依实现而定。 |
| eigh | 1 | 只想放假 · [PR#130](https://gitcode.com/cann/elec-ops-inspection/pull/130) · [code](https://gitcode.com/cann/elec-ops-inspection/tree/248cf09e66164d0567339ebc79c3c9acf792f962/2026_elec_operator_competition/preliminary/submissioins/jnu_op-zxfj/code/eigh) | 分布式 Householder、Sturm 二分、反迭代及反变换；检查残差/范数/相关性，坏列进入扩展精度和部分主元反迭代。 | 主体 AIV，大矩阵反变换才用 MIX/Cube；未见 Jacobi。 |
| eigh | 2 | FalseShare · 未找到公开源码 | 未找到公开源码，不做机制归因。 | 官方 PR/API 与 GitCode 全局检索均未定位对应公开实现；仅评价回执，不评价源码。 |
| eigh | 3 | answerend42 的队伍 · 未找到公开源码 | 未找到公开源码，不做机制归因。 | 官方 PR/API 与 GitCode 全局检索均未定位对应公开实现；仅评价回执，不评价源码。 |
| firecandidatedecodefusion | 1 | 注意力底下的队伍 · [PR#117](https://gitcode.com/cann/elec-ops-inspection/pull/117) · [code](https://gitcode.com/cann/elec-ops-inspection/tree/248cf09e66164d0567339ebc79c3c9acf792f962/2026_elec_operator_competition/preliminary/submissioins/nju_beyond-attention/code/firecandidatedecodefusion) | 帧/行/成对处理、地址表和先验复用，多个特定形状快路径与通用 832 候选回退。 | 大量 case 常量只证明工程覆盖。 |
| firecandidatedecodefusion | 2 | Delicate02 的队伍 · [PR#107](https://gitcode.com/cann/elec-ops-inspection/pull/107) · [code](https://gitcode.com/cann/elec-ops-inspection/tree/248cf09e66164d0567339ebc79c3c9acf792f962/2026_elec_operator_competition/preliminary/submissioins/xjtu_delicate02/code/firecandidatedecodefusion) | 小 tile 静态实现；Sigmoid 上溢风险检查与 RepairSmall，打包转置和通用大路径。 | 数值守卫是明确代码事实，修复收益未独立测量。 |
| firecandidatedecodefusion | 3 | 大爱仙尊 · [PR#123](https://gitcode.com/cann/elec-ops-inspection/pull/123) · [code](https://gitcode.com/cann/elec-ops-inspection/tree/248cf09e66164d0567339ebc79c3c9acf792f962/2026_elec_operator_competition/preliminary/submissioins/whu_hyosungsink/code/firecandidatedecodefusion) | 成对批次处理、先验共享、原生地址/索引生成，小中大及通用路径。 | 多种布尔模板不等于每种都被公开用例命中。 |
| lstsq | 1 | FalseShare · [PR#98](https://gitcode.com/cann/elec-ops-inspection/pull/98) · [code](https://gitcode.com/cann/elec-ops-inspection/tree/248cf09e66164d0567339ebc79c3c9acf792f962/2026_elec_operator_competition/preliminary/submissioins/zju_FalseShare/code/lstsq) | 小方阵驻留、RefinedSquare、Narrow/Orthogonal 与通用路径；NewtonGuard/CheckRefined 后转精确消元或 QR 尾部。 | 多路径含 MIX/Cube，不能把每次修正算作免费。 |
| lstsq | 2 | qunzhongjia 的队伍 · [PR#100](https://gitcode.com/cann/elec-ops-inspection/pull/100) · [code](https://gitcode.com/cann/elec-ops-inspection/tree/248cf09e66164d0567339ebc79c3c9acf792f962/2026_elec_operator_competition/preliminary/submissioins/qunzhongjia/code/lstsq) | 方阵专用与大形状协同，通用 FP32/BF16 Solver；BlockLu 主元与 Residual→Correct，通用 QR 修正。 | 未见另一算法回退；MIX 声明未核实实际 AIC 计算。 |
| lstsq | 3 | gcw_OTnEiQgj 的队伍 · [PR#111](https://gitcode.com/cann/elec-ops-inspection/pull/111) · [code](https://gitcode.com/cann/elec-ops-inspection/tree/248cf09e66164d0567339ebc79c3c9acf792f962/2026_elec_operator_competition/preliminary/submissioins/gcw_OTnEiQgj/code/lstsq) | 小方阵、普通/8核 LU 与通用 QR；部分主元、有限值检查及多次残差修正。 | 未见换算法回退；MIX 声明未核实实际 AIC 计算。 |
| pinv | 1 | 大爱仙尊 · [PR#121](https://gitcode.com/cann/elec-ops-inspection/pull/121) · [code](https://gitcode.com/cann/elec-ops-inspection/tree/248cf09e66164d0567339ebc79c3c9acf792f962/2026_elec_operator_competition/preliminary/submissioins/whu_hyosungsink/code/pinv) | RectPinv、compact/local/group/pipeline/window；RefineResident 修正并再认证，拒收后进入单边 Jacobi。 | window+cube 使用 INT8/FP32 Matmul 构造残差，需区分中间精度。 |
| pinv | 2 | FalseShare · [PR#97](https://gitcode.com/cann/elec-ops-inspection/pull/97) · [code](https://gitcode.com/cann/elec-ops-inspection/tree/248cf09e66164d0567339ebc79c3c9acf792f962/2026_elec_operator_competition/preliminary/submissioins/zju_FalseShare/code/pinv) | tiny、smallTeam、RowBlock 与通用路径；主元/截断范数门和残差修正，失败进入串行或协同 Jacobi。 | RowBlock 未全 accepted 时回退通用 Pinv，不能统一宣称所有分支走 Jacobi。 |
| pinv | 3 | 北枝 的队伍 · [PR#116](https://gitcode.com/cann/elec-ops-inspection/pull/116) · [code](https://gitcode.com/cann/elec-ops-inspection/tree/248cf09e66164d0567339ebc79c3c9acf792f962/2026_elec_operator_competition/preliminary/submissioins/beizhi/code/pinv) | cached 小矩阵/小组、199/200 专用及 256 Cube；AssessBatch/RefineInverse，!ok 进入 PinvJacobi。 | 当前维护版与原始比赛归档有明确差异，性能结论只限对应版本。 |
| safetybeltviolationgeometry | 1 | LinMingJing 的队伍 · 未找到公开源码 | 未找到公开源码，不做机制归因。 | 官方 PR/API 与 GitCode 全局检索均未定位对应公开实现；仅评价回执，不评价源码。 |
| safetybeltviolationgeometry | 2 | 伍六七-JLU · [PR#118](https://gitcode.com/cann/elec-ops-inspection/pull/118) · [code](https://gitcode.com/cann/elec-ops-inspection/tree/248cf09e66164d0567339ebc79c3c9acf792f962/2026_elec_operator_competition/preliminary/submissioins/JLU_op-wuliuqi/code/safetybeltviolationgeometry) | FP32/FP16 各六档覆盖全部 B；启动核与工作核分离；FP16 仅转换所需三列并保留分步舍入。 | Host 自述仍须用全形状测试验证。 |
| safetybeltviolationgeometry | 3 | Delicate02 的队伍 · [PR#106](https://gitcode.com/cann/elec-ops-inspection/pull/106) · [code](https://gitcode.com/cann/elec-ops-inspection/tree/248cf09e66164d0567339ebc79c3c9acf792f962/2026_elec_operator_competition/preliminary/submissioins/xjtu_delicate02/code/safetybeltviolationgeometry) | 分阶段 tiling，按真实 ratio/dtype/尾块选择原生宽 tile、常量特化和通用回退。 | 大量 tile class 不能当作独立性能证据。 |
| solve | 1 | ruby0451 的队伍 · [PR#115](https://gitcode.com/cann/elec-ops-inspection/pull/115) · [code](https://gitcode.com/cann/elec-ops-inspection/tree/248cf09e66164d0567339ebc79c3c9acf792f962/2026_elec_operator_competition/preliminary/submissioins/zju_ruby0451/code/solve) | tiny/small/列路径及通用 Solver；最大部分主元、列路径 Refine，通用大矩阵两遍残差求解。 | 未见失败后换算法；大路径也是 MIX_AIV，未见 Cube 计算。 |
| solve | 2 | 南工大果 · [PR#112](https://gitcode.com/cann/elec-ops-inspection/pull/112) · [code](https://gitcode.com/cann/elec-ops-inspection/tree/248cf09e66164d0567339ebc79c3c9acf792f962/2026_elec_operator_competition/preliminary/submissioins/hit_op-samerberry/code/solve) | tiny/batch/CoopGJ 与 SHAPE0 通用；按 diagDom/ill 选择普通或补偿残差，按残差范数决定 Refine。 | 未见换算法回退；AIV_ONLY 与 MIX_AIV 都未见 Cube 计算。 |
| solve | 3 | Helton 的队伍 · [PR#99](https://gitcode.com/cann/elec-ops-inspection/pull/99) · [code](https://gitcode.com/cann/elec-ops-inspection/tree/248cf09e66164d0567339ebc79c3c9acf792f962/2026_elec_operator_competition/preliminary/submissioins/zju_littlefairy/code/solve) | 小核、RefinedSquare 与多种 Direct/Orthogonal Cube 路径；NewtonGuard 失败后进入 ExactPanel64。 | 未见统一数值回退，不能将单一路径概括成全实现策略。 |
| splineconv | 1 | Zhanng-Whu 的队伍 · [PR#142](https://gitcode.com/cann/elec-ops-inspection/pull/142) · [code](https://gitcode.com/Zhanng-Whu/elec-ops-inspection/tree/f36ce9522ea84a30c5ce6e71ee7a473d53efff09/2026_elec_operator_competition/preliminary/submissioins/whu_Zhanng-Whu/code/splineconv) | 按 regime 分派；大档局部核权、中档高并行常驻、小档最小入口，保留通用实现。 | 第一轮已有详细对照；不重复宣称独立收益。 |
| splineconv | 2 | qunzhongjia 的队伍 · 未找到公开源码 | 未找到公开源码，不做机制归因。 | 官方 PR/API 与 GitCode 全局检索均未定位对应公开实现；仅评价回执，不评价源码。 |
| splineconv | 3 | 难敌 · [PR#109](https://gitcode.com/cann/elec-ops-inspection/pull/109) · [code](https://gitcode.com/cann/elec-ops-inspection/tree/248cf09e66164d0567339ebc79c3c9acf792f962/2026_elec_operator_competition/preliminary/submissioins/xjtu_qingmengyaxinghe/code/splineconv) | 单边/驻留 owner/通用邻接表；通用路径逐边逐槽计算并带补偿求和，支持可选输入。 | 公开 K=9 中/大档不命中 [2,2] 专用 resident，必须按通用路径评价。 |
| swiglu | 1 | SZKT · [PR#119](https://gitcode.com/cann/elec-ops-inspection/pull/119) · [code](https://gitcode.com/cann/elec-ops-inspection/tree/248cf09e66164d0567339ebc79c3c9acf792f962/2026_elec_operator_competition/preliminary/submissioins/SZKT_SZKT/code/swiglu) | 小 shape 纯 Vector，大 shape Cube+Vector；固定 Cube/驻留计划与 SplitK/FullK 回退。 | 同题三份都按规模换计算单元；具体 shape 表不等于通用阈值。 |
| swiglu | 2 | qunzhongjia 的队伍 · [PR#92](https://gitcode.com/cann/elec-ops-inspection/pull/92) · [code](https://gitcode.com/cann/elec-ops-inspection/tree/248cf09e66164d0567339ebc79c3c9acf792f962/2026_elec_operator_competition/preliminary/submissioins/qunzhongjia/code/swiglu) | 小规模 Vector，大规模 Cube 矩阵乘与 Vector 激活流水，双缓冲和成对投影；保留 ComputePlan 通用路径。 | 实现体量大，不能把模板数量当收益。 |
| swiglu | 3 | 我一定要赢口牙 · [PR#90](https://gitcode.com/cann/elec-ops-inspection/pull/90) · [code](https://gitcode.com/cann/elec-ops-inspection/tree/248cf09e66164d0567339ebc79c3c9acf792f962/2026_elec_operator_competition/preliminary/submissioins/shu_op-woyidingyaoyingya/code/swiglu) | 小规模 Vector、大规模 Cube；显式维护 half 各阶段舍入并保留顺序标量回退。 | 精度注释/回退需与实际分派核对，不能只看注释。 |
| treelinemindistance | 1 | gcw_OTnEiQgj 的队伍 · [PR#110](https://gitcode.com/cann/elec-ops-inspection/pull/110) · [code](https://gitcode.com/cann/elec-ops-inspection/tree/248cf09e66164d0567339ebc79c3c9acf792f962/2026_elec_operator_competition/preliminary/submissioins/gcw_OTnEiQgj/code/treelinemindistance) | 极小标量/单点单线段、短表 Brcb、较大点线对和空间路径；Host 预生成倒数乘子。 | 多档算法是代码事实，空间路径收益未独立复测。 |
| treelinemindistance | 2 | 只想放假 · [PR#131](https://gitcode.com/cann/elec-ops-inspection/pull/131) · [code](https://gitcode.com/cann/elec-ops-inspection/tree/248cf09e66164d0567339ebc79c3c9acf792f962/2026_elec_operator_competition/preliminary/submissioins/jnu_op-zxfj/code/treelinemindistance) | 静态标量域、压缩点线块、51bit 元数据；大输入 Morton 排序与保守包围盒筛选。 | 复杂空间索引只在大规模门控下启用。 |
| treelinemindistance | 3 | 难敌 · [PR#108](https://gitcode.com/cann/elec-ops-inspection/pull/108) · [code](https://gitcode.com/cann/elec-ops-inspection/tree/248cf09e66164d0567339ebc79c3c9acf792f962/2026_elec_operator_competition/preliminary/submissioins/xjtu_qingmengyaxinghe/code/treelinemindistance) | 多档点线分块/空间路径，另有宽行精确修正和共线平局证书。 | 精确修正范围依赖触发条件，不能归为全部输入都付的成本。 |

## 缺失实现的处理

未找到公开源码的四个回执不被其他名次或相似题目替代，也不据此推断这些队伍使用了什么技术。若后续官方仓库出现对应 PR，应新增独立复核事件，而不是回填未经验证的性能结论。

## 相关卡片

- [第二轮跨题高手习惯总结](cross_problem_expert_patterns.md)
- [用公开对照源码复盘 SplineConv 的结构差距](splineconv_leader_gap_review.md)
