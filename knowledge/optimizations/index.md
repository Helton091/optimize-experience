# 通用优化方法

- [用逐点差距选择结构优化目标](target_driven_optimization.md)：按负载差距选择能产生目标收益的结构轴，含公开八点自包含对照。
- [先写成本预算再写 kernel](write_cost_budget_before_kernel.md)：用字节、指令、DMA、波数、同步和精度构建可证伪预算。
- [负结果只关闭变体](negative_result_closes_variant_only.md)：边界结论必须带适用范围、推翻条件和证据。
- [先改布局和变换位置](layout_and_transform_placement.md)：共享变换可评估移到约减之后，减少重复拷贝与边界工作。
- [按每槽工作量设计 DMA 流水](dma_pipeline_and_makespan.md)：联合调节批量、槽数和 tile，并按最慢 block 验收。
- [按实际成本做非对称分带](cost_based_asymmetric_partition.md)：把 halo、尾块、归约角色和同步纳入每带成本。
- [跨核归约先减少交换载荷与同步](cross_core_reduction_payload_and_sync.md)：比较小 workspace、输出暂存、GM 往返和屏障的契约与成本。
- [归约慢时重构整条延迟链](restructure_reduction_latency_chain.md)：按依赖图减少中间态和回读，不用单项探针直接推算总收益。
- [特殊输入快路径检查真实值](device_checked_fast_path.md)：设备检查、通用回退和连续写回必须共同验证。
- [用最终输出误差预算决定数值路径](output_error_budget.md)：按输出误差传播评估 dtype；公开精度证据不足，当前为草稿。
- [AIV、Cube 与 MIX 按端到端总账选择](evaluate_compute_unit_end_to_end.md)：包含布局、交接、同步、发射、切换和封装的完整比较。
- [把 shape 特化维护成可审计配置](manageable_shape_specialization.md)：用声明式配置、模板和容量断言控制特化复杂度。
