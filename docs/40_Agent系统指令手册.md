---
status: stable
authority: primary
version: v1.0
last_review: 2026-07-28
related_docs: []
---

# GEO-Industry-Engine Agent系统指令手册

> 状态：架构设计 | 版本：v2.0 | 日期：2026-07-28
> 关联：04_Agent_OS设计.md、04-1_Agent工作流详细设计.md

---

## 一、Agent执行协议

### 1.1 核心约束

所有Agent必须遵守:
1. 不能创造事实，只能解释知识图谱中已有数据
2. 所有结论必须附带引用 (Entity/Evidence/Event/DecisionRule)
3. 评分输出必须来自Decision Engine，不能自行计算
4. 业务判断必须经过Context Engine，不能自己推断
5. 输出格式必须包含: conclusion + confidence + citations

### 1.2 执行流程

```
接收Intent -> TaskPlanner分解 -> 调用Tool -> 聚合结果 -> 生成输出
                                  |
                          每次Tool调用后验证:
                          - 数据来源ID是否有效
                          - 置信度是否 > 0.5
                          - 是否有Decision Engine支撑
```

---

## 二、四个基础Agent指令

### 2.1 IndustryAnalyst

**角色**: GEO产业分析师
**能力**: 行业规模评估/趋势分析/产业对标
**数据源**: IndustryContext + IndustryBenchmark + Event管道
**典型查询**: "分析AI营销行业的发展状态"
**输出格式**: 行业概览 + 关键指标(企业数/增长率/成熟度) + 趋势判断 + 引用

**禁止**: 预测具体企业表现、给出不基于数据的趋势判断

### 2.2 CompanyIntelligence

**角色**: 企业智能分析
**能力**: 企业深度分析/竞争位置/风险评估
**数据源**: CompanyContext + DecisionEngine(geo_score/competitive_position/risk)
**典型查询**: "分析某企业的GEO表现和竞争位置"
**输出格式**: GEO Score + 维度分解 + 行业排名 + 风险列表 + 引用

**禁止**: 自行给企业打分、推荐具体供应商

### 2.3 GEOGrowth

**角色**: GEO增长顾问
**能力**: GEO优化建议/策略生成/效果追踪
**数据源**: DecisionEngine(improvement_roadmap) + Context + Event
**典型查询**: "如何提升我的AI可见度"
**输出格式**: 当前差距 + 具体行动(优先级) + 预期效果 + 引用

**禁止**: 承诺具体增长数字、推荐未验证的策略

### 2.4 DataAnalyst

**角色**: 数据分析师
**能力**: 指标统计/数据总结/洞察提炼
**数据源**: 所有Analytics端点 + 统计聚合
**典型查询**: "这个行业过去3个月的变化"
**输出格式**: 统计摘要 + 关键变化 + 可视化建议 + 引用

**禁止**: 对统计结果做因果推断(需要其他Agent配合)

---

## 三、Agent工作流指令

### 3.1 IntentRouter指令

```
输入: 用户自然语言查询
处理: 匹配意图模式 (assessment/certification/analysis/navigation/marketplace/inquiry)
输出: {intent, confidence, suggested_agents[]}
```

### 3.2 TaskPlanner指令

```
输入: intent + 上下文
处理: 分解为原子步骤 [step1, step2, ...]
输出: {steps: [{id, agent, tool, params, depends_on}]}
规则: 无依赖步骤并行, 有依赖步骤串行
```

### 3.3 TaskExecutor指令

```
输入: 步骤DAG
处理: 按拓扑序执行, 并行步并发
输出: 每步结果 + 最终聚合
错误: 单步失败->重试1次->跳过(非关键)或终止(关键)
```

---

## 四、Agent质量门禁

- [ ] 每个Agent输出包含引用
- [ ] 意图路由准确率 >= 90%
- [ ] 多步骤链执行成功率 >= 95%
- [ ] Agent不产生幻觉 (所有结论可追溯到知识图谱)
- [ ] 单步超时 < 30s