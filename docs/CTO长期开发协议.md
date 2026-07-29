---
status: stable
authority: primary
version: v1.0
last_review: 2026-07-28
related_docs: []
---

# GEO-Industry-Engine 长期工程开发协议 v2.8

> **关联架构**: 详见 [06-11_系统关联架构设计](06-11_系统关联架构设计.md) — 六大系统数据流、Decision Engine路由、事件触发链
> 最后更新：2026-07-28 | 状态：stable | 权威等级：primary
> 替代：35_CTO架构冻结.md、00_项目宪章.md
> 关联：00_项目宪章.md、01_产品架构PRD.md、02_领域模型设计.md、05_技术架构.md、本文替代35_CTO架构冻结.md中过时的架构原则

---

## 零、最高指令

任何开发任务必须回答三个问题：

1. 这个功能服务哪个用户角色？（企业/个人/服务商/政府/机构/投资者/研究者）
2. 它增强五大系统哪个环节？（检测/认证/导航/资产/交易）
3. 它是否让 GEO 知识图谱、Context Engine 或 Decision Engine 变得更强？

三个问题不能全部回答的，不开发。

---

## 一、最高原则

### 1.1 事实优先级

以当前仓库事实为唯一开发依据。事实优先级：代码 > 测试 > API > 配置 > 文档 > 历史报告。
当文档与代码不一致时：先记录差异 → 判断哪一方符合架构冻结方向 → 修正错误方 → 同步更新权威文档。不得直接删除原有设计思想。

### 1.2 能力评估标准

废弃百分比完成度。改用三种状态：

| 状态 | 定义 | 判断标准 |
|------|------|----------|
| 可演示 | 前端→API→引擎→模型 全链路数据流通 | 用户输入→系统处理→有效结果返回 |
| 骨架就绪 | 代码结构正确但数据流中断或关键流程缺失 | 模块可导入，接口定义完整，但调用链未闭环 |
| 仅设计 | 只有文档，代码未开始 | 无对应模块或仅有占位文件 |

每个系统的评估追问不是有几个页面，而是：用户进入后能否形成认知闭环？闭环断在哪一步？

### 1.3 代码质量约束

- 核心模型测试覆盖率 ≥ 80%
- API 契约测试必须覆盖所有端点
- YAML 配置必须被代码实际读取，否则删除
- Agent 执行链必须可追踪（Intent → Plan → Tool → Result）
- 所有评分输出必须带解释（score + reason + improvement_action）

## 二、禁止事项

### 2.1 战略层面

1. 禁止擅自重新设计项目战略
2. 禁止删除原有五大用户系统
3. 禁止把 GEO-Industry-Engine 改造成单纯 GEO 评分工具
4. 禁止把项目压缩成单一 Assessment/Evaluation 产品
5. 禁止用技术层替代用户产品层
6. 禁止用技术架构层替代五大产品系统（技术架构层是后台能力组织方式，五大产品系统是用户入口，两者不可互换）
7. 禁止把能力层（产业情报）当成独立产品入口

### 2.2 产品层面

8. 禁止因模块暂未开发就从架构中删除
9. 禁止为了简洁删除未来必要模块
10. 禁止把首页做成 SaaS 菜单导航页——必须保留飞轮视觉和角色分流
11. 禁止把 TODO、占位接口写成已完成
12. 禁止未经验证就声称功能完成

### 2.3 工程层面

13. 禁止大量新建重复 Markdown 文档
14. 禁止将英文命名替换现有中文文档命名
15. 禁止重复建立已有 Entity/Context/Decision/Agent 能力
16. 禁止保留不工作的配置——写了 YAML 但代码未读取的，要么接入要么删除
17. 禁止 Agent 绕过 Context Engine + Decision Engine 直接生成业务结论
18. 禁止硬编码业务规则（评分权重、认证等级、推荐逻辑等）

### 2.4 变更判断

任何结构性变化必须先判断：是修复偏离，还是创造新架构？只有前者可自动执行，后者必须经过 CTO 审查。

## 三、项目最终战略定位

### 3.1 是什么

GEO-Industry-Engine 是：面向 GEO 产业生态的产业认知、身份、信任、知识、智能决策与生态连接基础设施。

### 3.2 不是什么

不是单纯 GEO 评分工具、不是单纯企业数据库、不是单纯行业地图、不是单纯交易平台、不是单纯认证平台、不是单纯 AI Agent 平台、不是单纯产业情报平台、不是单纯 SaaS 订阅产品。

### 3.3 终极目标

让 GEO 产业生态中的所有参与者——企业、个人、服务商、机构、政府/园区、投资者、研究者——能够：

> 找到自己 → 认识自己 → 证明自己 → 看懂产业 → 发现机会 → 识别风险 → 提前布局 → 建立连接 → 形成交易 → 数据反哺 → 持续成长

核心不是让用户使用一个工具，而是让用户在生态中找到自己的位置并持续进化。

---

## 四、最终产品架构

### 4.1 架构全景


> 备注：架构层次不绑定具体层数。层数可随系统演进增删，核心原则是用户产品层在上、智能能力层居中、数据基础设施层在下的三段式结构。用技术架构层统一指代，不再用七层或八层等数字锁定。

第一层：用户生态层 — 企业 / 个人 / 服务商 / 政府园区 / 机构 / 投资者 / 研究者

第二层：GEO 生态入口广场（首页）— 飞轮视觉 + 角色分流 + 快速评估 + 五大系统二级导航

第三层：五大产品系统 — 检测中心 / 认证中心 / 产业导航 / 数据资产中心 / 交易市场

第四层：智能能力层 — Decision Engine / Context Engine / Agent OS / 产业情报 / 生态行为感知

第五层：开放接口层 — REST API (57端点) / MCP Server
第六层：GEO 开放生态层 — Developer Platform / 第三方接入 / GEO Protocol

第七层：GEO 产业知识图谱 — Entity / Capability / Relationship / Event / Evidence / Trust

Entity 是多主体模型。以下主体均可拥有独立的 GEO 数字身份：企业(Company)、个人(Person)、机构(Organization)、产品(Product)、技术能力(Technology)、服务(Service)、项目(Project)。不同主体类型有不同的身份生命周期、认证路径和数据资产结构，但共享同一套知识图谱和引擎层。关系类型包括 owned_by、provides、uses、partners、certified_by、contributed_to 等，由 YAML 可扩展。

GEO 数字身份不是静态档案，而是动态产业生命体：过去 = Event 事件轨迹，现在 = Capability + Relationship + Trust + 可见度，未来 = Decision 预测的机会 + 风险 + 发展路径。身份随事件和数据积累持续演化，不属于任何一个系统专属，所有五大系统共享同一 Geo Identity。

数据质量维度：知识图谱的价值取决于数据质量。每个实体需评估五个维度：
完整度（信息覆盖率）、准确度（与事实一致性）、时效性（最后更新距今）、可信度（Evidence 支撑程度）、来源等级（官方>第三方>自行填报）。数据质量体系与认证体系天然关联：企业自行填报可信度低，第三方证明可信度高，官方数据最高。数据质量评分是 Trust Score 的基础输入之一。



身份快照（Identity Snapshot）：GEO 数字身份不是一次性画像，而是按时间戳记录的快照序列。每次 Context Engine 重新评估或 Decision Engine 生成报告时，系统自动生成一条 IdentitySnapshot，记录该时刻的 Entity 状态、Capability 集合、Relationship 图、Trust Score、GEO Score 及当前产业位置。快照序列是趋势预测、风险预警、机会发现和成长路线的基础数据输入。快照本身不是一个独立 Engine，而是 Entity + Event + Context + Decision 的自然产物。
第八层：数据基础设施 — PostgreSQL / Redis / YAML配置中心 / Analytics

### 4.2 首页定位

首页结构（自上而下）：
1. 飞轮视觉（数据→认知→信任→连接→交易→数据）— 让用户一眼看懂生态运转逻辑
2. 快速检测入口（搜索框 + 开始评估按钮）— 最低门槛进入点 快速检测返回简版GEO身份卡（企业名称+行业+等级+可见度分数），点击详情跳转检测中心获取完整四层报告。快速检测与完整检测共享同一Decision Engine，区别仅在前端展示深度。
3. 角色分流区 — 企业入口、个人入口、服务商入口、机构入口
4. 五大系统二级导航 — 检测中心、认证中心、产业导航、数据资产中心、交易市场

首页不是菜单。首页的意义是看明白生态 + 快速进入。

### 4.3 角色差异化首页

不同角色进入首页后，看到的飞轮放大环节不同：
- 企业：放大认知和信任 + 我的GEO位置卡片
- 个人：放大认知和连接 + 我的能力等级卡片
- 服务商：放大信任和连接 + 我的认证状态卡片
- 政府：放大知识和数据 + 区域产业概览卡片
- 投资者：放大知识和连接 + 新兴赛道卡片
- 研究者：放大知识和数据 + 数据导出入口

---

## 五、五大产品系统详细定义

### 5.1 检测中心 · GEO 战略评估

定位：GEO 产业战略评估与数字身份入口。外部展示名称保留检测中心，加副标题 GEO 战略评估。

四层展示结构：

| 层次 | 名称 | 回答的问题 | 数据来源 |
|------|------|-----------|----------|
| 第一层 | 身份与位置 | 我是谁？在产业中排哪里？ | Entity + Context + Trust Score |
| 第二层 | 机会发现 | 未来12个月能抓住什么？ | Decision + 产业情报(机会) |
| 第三层 | 风险预警 | 谁在超越我？什么在威胁我？ | Decision + 产业情报(风险) |
| 第四层 | 行动路线 | 该做什么？分几步？ | Decision(ROADMAP) + Agent |

硬约束：禁止检测中心独立计算评分——所有数据必须来自 Context Engine 和 Decision Engine。每个评分必须带 reason 和 improvement_action。前端页面只做展示不做计算。

GEO 数字身份卡标准展示格式：

企业身份卡示例：GEO ID + 企业名称 + 行业归属 + 能力标签(Lv) + 可信等级(L0-L4) + 行业排名(Top X%) + AI可见度分数 + 未来机会方向。
个人身份卡示例：GEO ID + 姓名 + 职业身份 + 能力标签 + 认证等级 + 行业影响力排名。

GEO 数字身份 = Entity(是谁) + Capability(会什么) + Relationship(连接谁) + Evidence(证明什么) + Event(发生过什么) + Trust(可信程度) + Decision(系统如何评价)。所有五大系统的展示层必须复用此身份卡组件，保证一致性。

### 5.2 认证中心 · 可信身份证明

定位：GEO 产业生态的可信身份与能力证明体系。

三维认证结构：

| 维度 | 内容 | 配置方式 |
|------|------|----------|
| 对象 | 企业、个人、服务商、机构、其他 | YAML 可扩展 |
| 等级 | L0(未认证)→L1(基础身份)→L2(生态认证)→L3(专业能力)→L4(行业权威) | YAML 可配置每级解锁功能 |
等级含义：L0=未认证（无权限）| L1=基础身份验证（可查看基础数据）| L2=生态认证（可展示认证标识+参与产业导航）| L3=专业能力认证（可进入交易市场+获得能力标签）| L4=行业权威认证（可成为标准制定者+获得生态治理权）。每级解锁的具体功能由 YAML 配置，非硬编码。

| 类型 | 身份认证、能力认证、行业贡献认证 | YAML 可新增类型 |

审核流程：用户提交 → AI 自动初审（验证数据完整度 + 证据有效性）→ 人工复审（行业专家）→ 发放数字证书 → 更新 Trust Score → 定期复核（2年有效期）。

关联关系：认证结果必须统一展示在企业画像、搜索列表、产业导航、服务商页面、交易市场、GEO 数字身份卡。认证不是孤立页面，是贯穿整个系统的信任基础设施。

### 5.3 产业导航 · 产业数字地图

定位：GEO 产业世界地图——产业数字孪生系统。不是静态展示，而是对现实 GEO 产业世界的数字化建模：数据采集 → Entity/Capability/Relationship/Event/Evidence → 数字化产业模型 → Context 理解 → Decision 预测 → 用户行动。这是项目的长期护城河。

五张核心地图（MECE 设计，模块化，可扩展）：

1. 产业生态地图（9层价值链）— 产业价值链节点 + 公司归属 + 关系边 + 变化方向 + 时间轴
2. 商业赚钱地图（四栏矩阵）— 企业按 GEO Score + 增长速率自动落位
3. 运营流程地图（8阶段）— 从数据建设到交易闭环，企业当前阶段可视化
4. 地域生态地图（区域分布）— 按省/市/园区维度的产业分布 + 热力图
5. 发展方向地图（三线预测）— 保守线（现有趋势）/ 增长线（机会发现）/ 突破线（新兴赛道）

核心原则：产业导航不是地图，而是产业数字孪生。地图展示的是快照，数字孪生展示的是理解 + 预测。底层由 Entity + Relationship + Capability + Event + Context Engine 实时驱动。不同角色看到不同侧重。

### 5.4 数据资产中心 · 知识资产沉淀


五张地图的关系：五张地图不是五个独立模块，而是同一 GEO 产业知识图谱的五种视图(View)。底层共享 Entity + Relationship + Capability + Event，上层按用户目标和角色切换视角。禁止为每张地图单独建数据模型或重复开发。一张地图的数据更新，所有视图同步刷新。
定位：GEO 产业生态的数据资产与知识沉淀中心。可展示、可评论、可通过 API 访问（权限范围内）。

用户可见：GEO 数字资产概览 / 数据完整度评分 / 数据缺口分析 / 数据可信度评估 / 资产成长趋势 / 补充建议（按影响力排序）。

系统必须回答：你现在拥有什么？你缺什么？哪些缺失影响 GEO 表现/认证/产业机会？下一步最值得补充什么？

反哺关系：数据资产必须持续反哺 Context Engine、Decision Engine、Agent OS、认证体系、产业导航、交易市场，形成数据飞轮。

### 5.5 交易市场 · 生态连接器

定位：GEO 产业生态连接器。当前阶段保留完整架构设计和接口预留，不强行提前完成。

未来完整能力：需求发布 / 服务商展示 / 能力匹配 / 需求匹配 / 服务交易(订单→交付→评价→结算) / 交易数据反哺。

关联关系：交易不是独立电商。必须与 Entity、Certification、Trust、Capability、Evidence、Decision Engine 建立关系。

---

## 六、智能能力层详细定义

### 6.1 Decision Engine · 可解释决策中枢

定位：整个系统的智能决策中枢。不是检测中心专属。

核心原则：Decision Engine 不直接拥有业务逻辑。输入是 Entity + Context + Evidence，输出是 Recommendation + Action + Roadmap。

可解释原则（最高优先级）：所有评分输出必须包含 score + reason + improvement_action + evidence_chain。禁止黑盒评分。

反馈闭环（P2 优先级）：Decision Engine 需要从"分析→推荐"升级为"推荐→执行→结果→学习"的完整闭环。系统建议被用户执行后，追踪评分是否提升，根据实际效果调整模型参数。有反馈闭环的 Decision Engine 才是智能系统，否则只是咨询师。

服务范围：为五大系统提供评分、评估、预测、机会发现、风险识别、排名、匹配、推荐、路线规划。

时间维度（P2 优先级）：Decision Engine 需逐步加入时间变化追踪能力（GEO Growth Timeline），追踪同一实体在不同时间点的评分变化趋势，分析变化原因（内容增减、认证变化、关系变化、事件影响），实现提前发现机会和风险的预测能力。

配置化：所有评分权重从 YAML 配置读取。当前 config/scoring/ 下的 YAML 必须接入 Decision Engine 的实际计算代码。不接入的删除。

### 6.2 Context Engine · 产业上下文引擎

定位：将 Entity + Relationship + Capability + Event + Evidence 转化为可理解、可计算、可查询、可推荐的产业智能上下文。

核心能力：Company Context / Industry Context / Capability Context / Natural Query（中文查询→Intent识别→Entity检索→关系扩展→Evidence验证→Ranking）。

检索策略：第一阶段使用 PostgreSQL + JSONB + 全文搜索。设计统一的 Retrieval Interface 兼容未来 Vector DB、Neo4j、Hybrid Search。

### 6.3 Agent OS · 智能执行层

当前真实状态：骨架就绪。

- 4 个 Agent 已注册：IndustryAnalyst、CompanyIntelligence、GEOGrowth、DataAnalyst
- 意图路由工作正常（关键词匹配）
- 但每个 Agent 目前只调用一个 Tool，没有多步骤推理
- Memory 接口定义了但未被任何 Agent 调用
- task_planner.py 存在但无 Agent 使用

正确执行链：用户问题 → Intent Router → Task Planner（拆解步骤）→ Step1: Context Tool 获取上下文 → Step2: Decision Tool 计算评分/机会/风险 → Step3: 聚合分析生成报告 → Step4: Memory.remember（沉淀）→ 返回结构化结果。

下一步目标：不让 4 个 Agent 同时做面子工程。优先让一个 Agent（IndustryAnalyst）跑通完整多步骤链路。一个跑通后其他三个复用同一框架。

硬约束：禁止 Agent 直接访问数据库 / 禁止绕过 Context Engine 和 Decision Engine / 禁止依赖 LLM 幻觉输出 / Agent 只能通过 Tool → Context/Decision Engine → 知识图谱获取数据。

Agent 定位约束：Agent 不是专家，Agent 是产业知识的解释者。所有 Agent 输出必须引用 Entity、Evidence、Event 或 Decision Rule 作为依据，不得创造知识图谱中不存在的事实。

### 6.4 产业情报系统 · 共享能力层

定位：竞争情报 + 机会情报 + 风险情报。不设独立第六入口，作为共享能力渗透到五大系统。

| 模块 | 服务对象 | 渗透方式 |
|------|----------|----------|
| 竞争情报 | 检测中心、导航 | 竞品变化、位置变化、份额变化 |
| 机会情报 | 检测中心、导航、资产 | 行业趋势、新兴赛道、产业空白 |
| 风险情报 | 检测中心、资产 | 行业风险、技术风险、退化预警 |

数据来源：Event + Relationship + Industry + Context + Decision + Agent。

### 6.4.1 渗透机制

产业情报不是独立系统，不设独立前端页面。其数据流为：

外部数据源 → Event 采集 → 写入 GEO 知识图谱（Entity/Relationship/Event）→ Context Engine 读取 → Decision Engine 计算 → 五大系统前端展示。

各系统的情报消费路径：
- 检测中心：Decision Engine 调用情报数据计算竞争位置、风险等级、机会评分
- 认证中心：情报数据作为 Evidence 来源之一，影响 Trust Score 自动调整
- 产业导航：情报数据驱动五张地图的趋势线和变化方向
- 数据资产中心：情报事件作为建议补充的数据来源引用
- 交易市场：情报数据辅助能力匹配和服务商推荐

禁止各系统直接调用情报 API。情报数据只通过知识图谱和 Decision Engine 间接消费。

### 6.5 生态行为感知系统

定位：感知 GEO 产业生态的变化。不是普通 BI。感知维度：谁进入产业、谁在成长、谁在找机会、哪些能力增长、哪些行业变化、哪些关系形成。
当前轻量事件模型保留，不过度建设复杂 BI。但必须作为长期数据飞轮基础设施。

---

## 七、用户角色驱动模型

核心区分：五大系统是能力组织方式，用户角色是体验组织方式。系统回答"平台能做什么"，角色回答"用户为什么来、怎么走"。首页按角色分流，系统内部按角色切换视图，开发时禁止用系统菜单替代角色体验路径。

系统设计的驱动逻辑不是"五大系统 → 用户角色"，而是反过来：

用户角色 → 用户目标 → 进入系统 → 看到不同视图 → 触发不同能力。

GEO-Industry-Engine 的最大价值不是功能，而是让 GEO 生态中的每一个参与者找到自己的位置。

### 7.1 角色分类

| 角色大类 | 子角色 | 核心需求 | 推荐路径（非强制路由） |
|----------|--------|----------|----------|
| 企业 | 企业老板、市场负责人、GEO负责人 | 知道AI可见度+提升+找服务商 | 首页→检测中心→认证→导航 |
| 个人 | GEO从业者、顾问、学习者 | 建立职业身份+能力认证+找机会 | 首页→检测中心→认证→资产 |
| 服务商 | GEO服务商、内容机构、技术公司 | 展示能力+获得认证+找到客户 | 首页→认证中心→交易市场 |
| 政府/园区 | 产业管理部门 | 产业分布+企业能力地图+趋势 | 首页→产业导航→产业情报 |
| 机构 | 投资机构、行业协会、研究机构 | 发现机会+行业分析+数据导出 | 首页→产业导航→数据资产 |
| 平台生态 | 数据贡献者、Agent开发者 | API接入+数据贡献+生态参与 | MCP+API |

### 7.2 角色差异化首页

- 企业：飞轮放大认知和信任 + 我的GEO位置卡片
- 个人：飞轮放大认知和连接 + 我的能力等级卡片
- 服务商：飞轮放大信任和连接 + 我的认证状态卡片
- 政府：飞轮放大知识和数据 + 区域产业概览卡片
- 投资者：飞轮放大知识和连接 + 新兴赛道卡片

---

## 八、配置化与模块化原则

### 8.1 配置化范围

凡是未来可能变化的规则优先配置化：评分权重、决策模型参数、认证等级规则及解锁功能、审核规则、权限矩阵、套餐定义、支付规则、交易分类、匹配权重、产业分类、情报权重、风险阈值、机会阈值、推荐规则、Agent Prompt、Agent Workflow。

### 8.2 配置目录结构

config/
  scoring/default/      ← 默认配置（兜底）
  scoring/industry/     ← 按行业覆盖（healthcare/education等）
  certification/        ← 认证配置
  pricing/              ← 定价配置
  marketplace/          ← 交易市场配置
  competitive/          ← 产业情报配置
  analytics/            ← 行为感知配置

### 8.3 硬约束

所有 config/ 下的 YAML 必须要么被代码实际读取，要么删除。不允许存在看起来有配置但实际未使用的误导状态。

当前待解决：config/scoring/ 下 6 个 YAML 尚未接入 Decision Engine 的实际计算代码。P0 修正项。

### 8.4 统一权限体系

config/pricing/permissions.yaml 已定义权限矩阵，但协议未明确权限架构。补充如下：

权限模型：User → Role → Organization → Permission → Data Scope → Action。

| 角色 | 可见范围 | 可操作 | 数据导出 |
|------|----------|--------|:--:|
| Free用户 | 自己的评估结果 | 查看 | ❌ |
| Growth/Pro | 自己+授权关联方 | 查看+补充数据+申请认证 | ⚠️ 受限 |
| 服务商 | 客户的授权数据 | 查看+分析+生成报告 | ⚠️ 客户授权 |
| 政府/园区 | 区域聚合数据 | 查看+导出+趋势分析 | ✅ 聚合 |
| 机构 | 授权行业数据 | 查看+API调用 | ✅ 按协议 |
| 开发者 | API配额内 | 调用 | ✅ 按配额 |
| 管理员 | 全部 | 管理 | ✅ |

### 8.5 多租户多视角体系

代码中 tenant_id 已存在于所有核心模型。协议明确多租户战略：

同一 Entity 在不同租户/区域/行业视角下可以有不同的 Context。例如：同一企业，全球视角是"AI公司"，中国视角是"人工智能产业企业"，上海视角是"本地重点企业"，投资机构视角是"潜力标的"。多租户不是数据隔离，而是多维度产业认知。这与"同一套引擎复制到不同产业"的长期目标一致。

### 8.6 最终目标

同一套 GEO-Industry-Engine 可以根据行业、企业类型、地区、阶段进行快速配置与复用。医疗 GEO 和教育 GEO 使用不同的评分配置，不需要修改代码。

---


### 8.4 安全与权限架构

认证策略：采用 JWT（JSON Web Token）作为默认认证方案，同时预留 OAuth2 扩展接口供未来第三方登录。所有 API 端点（除公开首页外）强制认证。

授权模型：RBAC（基于角色的访问控制）——角色分为平台管理员、企业管理员、企业成员、认证审核员、普通用户、匿名访问者。每个角色绑定预设权限集合，权限由 YAML 配置管理（config/permissions/*.yaml）。

数据隔离：多租户数据隔离通过 tenant_id 字段实现行级安全。数据库查询层统一注入 tenant_id 过滤条件，禁止在业务代码中手动拼接租户过滤。同一租户内，企业成员只能访问本企业数据（organization scope），平台管理员可跨租户查看（platform scope）。

API 安全：所有请求强制 Rate Limiting（按用户/IP 双维度）、CORS 白名单控制、请求体大小限制。敏感操作（认证审核、支付、数据导出）需二次验证。

数据隐私：企业/个人数据所有权归数据主体。数据导出、删除、匿名化功能必须支持。第三方 API 访问需数据主体明确授权。


### 8.5 配置生命周期管理

配置不是一次性写入的静态文件。采用三级目录结构：

- active/ — 当前生效的配置（被代码实际读取）
- experiments/ — 实验版本（A/B测试、新模型调参）
- deprecated/ — 废弃版本（保留历史参考，不再被代码读取）

当前 config/ 目录的 14 个 YAML 需逐步整理到上述结构。config/scoring/ 下 6 个未接入的 YAML 归属 experiments/，接入验证后移入 active/。

同一引擎复制到不同产业（医疗 GEO / 教育 GEO）时，通过切换 active/ 下的产业配置包实现，不修改代码。

## 九、核心战略飞轮

完整飞轮：数据进入 → Entity/Capability/Relationship/Event/Evidence → 产业知识形成 → Context Engine 理解产业 → Decision Engine 可解释评估与预测 → 产业情报持续感知 → Agent OS 多步骤智能执行 → 用户获得认知（通过五大产品入口：检测/认证/导航/资产/交易）→ 用户行为与新事件回流 → 数据持续增长 → Context 更准确 → Decision 更智能 → 生态持续增长。

飞轮原则：飞轮的任何一环断裂，整个系统的价值就会退化。不能只建设检测和评分而忽略信任和连接。用户行为必须回流到数据层形成闭环。每轮循环数据质量提升，智能能力随之提升。

### 9.3 用户成长生命周期模型

飞轮描述的是系统如何运转。生命周期描述的是用户在系统中如何长期成长：

| 阶段 | 名称 | 用户行为 | 系统提供 | 数据沉淀 |
|:--:|------|----------|----------|----------|
| 0 | 未知 | 不知道AI时代自己的位置 | 首页飞轮+快速检测入口 | — |
| 1 | 被发现 | 进入检测中心 | GEO数字身份+基础评估 | Entity+基础评分 |
| 2 | 被理解 | 补充数据资产 | 企业画像+能力画像+关系画像 | Capability+Relationship |
| 3 | 被认可 | 进入认证体系 | 可信身份+等级证书 | Certification+Trust+Evidence |
| 4 | 被连接 | 进入产业导航 | 合作伙伴发现+市场机会 | Relationship+Event |
| 5 | 被放大 | 进入交易市场 | 商业机会+生态连接 | Order+Review |
| 6 | 持续优化 | 数据反哺+重新评估 | 新机会+新风险+新路线 | 全部模型更新 |

每个阶段的跃迁由 Decision Engine 评估触发。用户不是买一个功能，而是在 GEO 生态中成长。

> 区分：上述生命周期描述的是产业实体在 GEO 生态中的成长，覆盖 GEO 数字身份从创建到演化的过程。平台用户账户（注册/登录/权限）是另一条独立的管理生命周期，不混入此模型。一个平台用户可管理多个 GEO 身份，一个 GEO 身份可被多个平台用户协作管理。

---

## 十、开发流程规范

### 10.1 开发前检查清单

任何新功能开发前必须确认：
1. 是否已阅读相关领域的权威文档？
2. 该功能服务哪个用户角色？
3. 该功能增强五大系统哪个环节？
4. 该功能是否让知识图谱/Context/Decision 变得更强？
5. 该功能是否已有现有代码可复用？（先检查再新建）
6. 是否需要新增 YAML 配置？是否已接入代码？
7. 是否需要新增数据库字段？是否已更新 Migration？
8. 是否需要新增 API？是否已在 main.py 注册？

### 10.2 代码审查标准

- 业务规则必须在 YAML 或数据库配置中，不得硬编码
- 评分输出必须包含 score + reason + improvement_action
- API 返回必须符合 Schema 定义
- 新增模块必须在对应 __init__.py 注册
- 测试覆盖率 ≥ 80%（核心模型和 API 路由）

### 10.3 架构冻结点

以下事项已冻结（v2.2），只能补实现、优化性能、完善体验，禁止重新设计：

| 冻结项 | 说明 |
|--------|------|
| ✅ 五大用户系统 | 检测中心/认证中心/产业导航/数据资产/交易市场 — 不增不减 |
| ✅ Entity 核心模型 | Entity/Capability/Relationship/Event/Evidence/Trust — 不可删除 |
| ✅ 技术架构层 | 用户生态→入口广场→五大系统→智能能力→开放接口→开放生态→知识图谱→数据基础设施 |
| ✅ Context Engine 定位 | 产业上下文引擎，统一检索接口 |
| ✅ Decision Engine 定位 | 可解释决策中枢，配置驱动 |
| ✅ Agent OS 方向 | 多步骤执行链，不绕过引擎层 |
| ✅ 配置化原则 | 业务规则 YAML 驱动，禁止硬编码 |
| ✅ 首页飞轮+角色分流 | 不是菜单导航页 |
| ✅ 产业情报为共享能力层 | 不独立成第六入口 |

### 10.4 新功能准入规则（Feature Admission Rule）

任何新增功能必须通过四问：

1. 服务哪个角色？（企业/个人/服务商/政府/机构/投资者/研究者）
2. 增强哪个系统？（必须属于五大系统之一）
3. 增强哪个底层能力？（至少一个：Entity/Context/Decision/Agent/Knowledge Graph/Analytics）
4. 是否产生长期资产？（一次性页面→拒绝；增加数据/关系/模型/知识/反馈→接受）

四问不能全部通过的，不开发。

### 10.5 项目宪章 §架构治理

涉及核心模型、API 接口签名、YAML 配置结构、产品入口的变更，必须：
1. 说明变更原因 → 2. 影响分析 → 3. CTO 审查 → 4. 更新关联文档 → 5. 更新 docs/索引.md → 6. Git Commit 包含变更说明。

---


### 10.3 测试策略

核心模型定义：domain/ 下 6 个领域模型（entity.py, capability.py, relationship.py, event.py, evidence.py, trust.py）以及 decision/ 下评分引擎为核心模型，覆盖率目标 ≥ 80%。

测试分层：
- 单元测试：覆盖领域模型方法、评分算法、配置解析器、Agent Tool 逻辑。不依赖外部服务。
- 集成测试：覆盖 API 端点全链路（请求→路由→引擎→模型→响应）。需要 PostgreSQL。
- E2E 测试（远期）：Playwright 驱动的用户流程测试。当前阶段不强制。

当前问题处理：13 个集成测试中 6 个因 PostgreSQL 未启动而失败。不是测试逻辑错误，是环境依赖问题。修复方案：CI 流程中自动启动 docker-compose postgres，或在测试脚本中增加 PostgreSQL 可用性检测并 skip 不可用测试。

测试门禁：PR 合并前必须通过单元测试 + 集成测试（数据库可用时）。覆盖率不达标阻塞合并。


### 10.4 部署与运维架构

当前部署：infrastructure/docker-compose.yml 定义了 PostgreSQL + Redis 开发环境。本地开发通过 docker-compose up 启动基础设施，前后端分别通过 npm run dev 和 uvicorn 启动。

目标环境：
- 开发环境：本地 Docker Compose
- 预发布环境：单机 Docker Compose（或云服务器）
- 生产环境（远期）：Kubernetes + 云数据库（PostgreSQL 托管服务）+ Redis 托管服务

CI/CD 方向：Git push → GitHub Actions / GitLab CI → 自动运行 lint + 单元测试 + 集成测试（docker-compose up postgres）→ Build 验证（前端 Next.js build + 后端 Python compile check）→ 部署到目标环境。

监控预留：预留 Prometheus metrics 端点（/metrics）和健康检查端点（/health）。当前阶段不强制接入 APM。

数据库运维：Migration 通过 Alembic 管理。备份策略（远期）：PostgreSQL pg_dump 定时任务 + WAL 归档。

## 十一、当前执行任务

当前阶段：架构设计阶段。所有编码任务冻结。优先完成设计补全。

### 11.1 当前阶段：架构设计补全（对应附录 C.2）

1. 五大系统前端信息架构设计 — 完整页面树 + 导航结构 + 组件层级 + 每页数据来源标注
2. 五大系统用户流程设计 — 每类角色的完整任务路径
3. YAML 配置 Schema 设计 — 14 个 YAML 的精确字段结构定义
4. API 契约完整定义 — 57 个端点的完整 Request/Response Schema
5. 数据库 Migration 策略设计 — 初始 Schema 定稿 + 版本管理 + 种子数据

### 11.2 编码阶段启动条件

以上 5 项架构设计全部定稿后，方可启动编码。启动前需 CTO 确认所有设计产出已冻结。

### 11.3 编码 P0（设计完成后，对应附录 C.3）

1. 6 个评分 YAML 接入 Decision Engine（前置：C.2-3）
2. Agent 多步骤链路（前置：C.2-4）
3. 首页改造为飞轮+角色分流（前置：C.2-1）

### 11.4 专项审查（全阶段持续）

- 检查所有 config/ YAML 是否被代码实际读取
- 检查所有 Agent 执行链是否完整
- 检查所有 API 是否已注册到 main.py
---

## 十二、文档治理

### 12.1 权威文档列表

| 文档 | 领域 | 状态 |
|------|------|:--:|
| 00_项目宪章.md | 项目宪法 | stable |
| 01_产品架构PRD.md | 产品设计 | stable |
| 02_领域模型设计.md | 知识图谱 | stable |
| 03_数据架构.md | 数据设计 | stable |
| 04_Agent_OS设计.md | Agent设计 | stable |
| 05_技术架构.md | 技术架构 | stable |
| 08_API接口规范.md | API规范 | stable |
| 35_CTO架构冻结.md | 架构冻结 | stable |
| 本文件 | 开发总控协议 | primary |

### 12.2 Codex 读取顺序

第一优先级：本文件 → 第二：00_项目宪章.md → 第三：对应领域设计文档 → 第四：08_API接口规范.md + 03_数据架构.md → 第五：历史讨论和报告。

### 12.3 文档维护规则

代码变更涉及架构的必须同步更新关联文档。文档版本使用 Git 历史管理。docs/索引.md 保持最新。废弃文档移动到 docs/archive/ 不得直接删除。

---

---

## 十三、开放生态战略

### 13.1 三层开放体系

GEO-Industry-Engine 的长期形态不是封闭平台，而是产业基础设施：

| 层级 | 能力 | 当前状态 |
|------|------|:--:|
| REST API | 57 端点，覆盖所有五大系统的数据读写 | 骨架就绪 |
| MCP Server | Agent 可调用的上下文、决策、分析工具 | 基础框架就绪 |
| Developer Platform | 第三方创建 GEO Agent、构建行业应用、接入企业系统 | 仅设计 |

### 13.2 GEO Protocol（远期）

未来定义统一的 GEO 数据交换协议，使第三方可以：调用 GEO 数据、创建 GEO Agent、构建行业应用、接入企业自有系统。目标是形成 GEO-Industry-Engine → GEO Platform → GEO Ecosystem 的演进路径。当前阶段不投入开发。

---

## 十四、商业化架构

### 13.1 分层模型

Free(免费版-个人/探索者) / Growth(成长版-中小企业) / Pro(专业版-中型企业/服务商) / Business(商业版-大型企业/机构) / Enterprise(企业版-政府/园区/平台)。

### 13.2 原则

商业化模块属于生态变现基础设施，不属于产品核心价值层。优先级链：产业知识 → 用户价值 → 生态连接 → 商业化。不能让 Pricing/Payment/Subscription 反过来主导核心产业知识架构。不能让 Codex 看到付费模型就认为这是 SaaS 产品。权限模型已设计，YAML 可配置，但暂不开发支付集成。会员权限通过 YAML 配置控制功能可见性。

---

> 本协议是 GEO-Industry-Engine 所有开发活动的最高准则。任何偏离必须经过 CTO 审查。


---

# 附录

## 附录A：代码模块全景映射

本附录将协议中的每个架构概念映射到当前仓库的具体文件路径。

### A.1 领域模型（Domain Layer）→ 知识图谱

| 概念 | 领域模型 | ORM 模型 | Schema |
|------|----------|----------|--------|
| Entity | domain/entities/entity.py | models/entity.py | schemas/entity.py |
| Company | domain/entities/company.py | models/company.py | schemas/company.py |
| Industry | domain/entities/industry.py | models/industry.py | schemas/industry.py |
| Capability | domain/capability/capability.py | models/capability.py | schemas/capability.py |
| Relationship | domain/relationship/relationship.py | models/relationship.py | schemas/relationship.py |
| Event | domain/event/event.py | models/event.py | — |
| Evidence | domain/evidence/evidence.py | models/evidence.py | schemas/evidence.py |
| Trust | domain/trust/trust.py | — | — |
| Certification | — | models/certification.py | schemas/certification.py |
| User | — | models/user.py | schemas/user.py |
| Subscription | — | models/subscription.py | schemas/subscription.py |
| Order | — | models/order.py | — |
| Payment | — | models/payment_transaction.py | schemas/payment.py |
| Market Demand | — | models/market_demand.py | schemas/marketplace.py |
| TransactionReview | — | models/transaction_review.py | — |
| Competitor | — | models/competitor.py | schemas/competitor.py |
| AnalyticsEvent | — | models/analytics_event.py | schemas/analytics.py |

### A.2 引擎层 → 代码模块

| 架构概念 | 文件路径 | 行数估值 |
|----------|----------|:--:|
| Context Engine | context/engine.py + builders/ (3) + retrieval/ (3) + ranking/ (3) + schemas/ (1) | 11 files |
| Decision Engine | decision/engine.py + models/ (12) + scoring/ (2) + explanation/ (1) + recommendation/ (1) | 19 files |
| Agent Framework | agents/core/ (2) + agents/agents/ (4) + tools/ (2) + router/ (1) + planner/ (1) | 10 files |
| MCP Server | mcp/server.py + mcp/tools/ (2) | 3 files |

### A.3 API 路由 → 系统映射

| API 模块 | 路由前缀 | 服务系统 | 主要端点 |
|----------|----------|----------|----------|
| context.py | /api/v1/context/ | 检测中心、导航 | GET company/{id}, POST query |
| decision.py | /api/v1/decision/ | 检测中心 | GET company/{id}, POST analyze |
| agent.py | /api/v1/agent/ | Agent | POST analyze, GET list |
| certification.py | /api/v1/certification/ | 认证中心 | POST apply, GET levels/status, PUT review |
| companies.py | /api/v1/companies/ | 导航、检测 | GET list/{id} |
| industries.py | /api/v1/industries/ | 导航 | GET list/{id} |
| entities.py | /api/v1/entities/ | 资产 | GET list/{id} |
| relationships.py | /api/v1/relationships/ | 导航 | GET list |
| evidence.py | /api/v1/evidence/ | 资产、认证 | GET list, POST create |
| marketplace.py | /api/v1/marketplace/ | 交易市场 | GET demands |
| intelligence.py | /api/v1/intelligence/ | 产业情报 | GET competitors |
| analytics.py | /api/v1/analytics/ | 行为感知 | POST events/batch |
| mcp_router.py | /api/v1/mcp/ | 开放生态 | GET tools |
| admin.py | /api/v1/admin/ | 管理后台 | GET configs/stats |
| subscriptions.py | /api/v1/subscriptions/ | 商业化 | CRUD |
| payments.py | /api/v1/payments/ | 商业化 | 占位 |
| auth.py | /api/v1/auth/ | 通用 | POST register/login |
| users.py | /api/v1/users/ | 通用 | GET me |

### A.4 前端页面 → 系统映射

| 路由 | 大小 | 对应系统 | 数据来源 | 状态 |
|------|:--:|----------|----------|:--:|
| / (首页) | 178B | 入口广场 | — | 骨架就绪（需改造为飞轮+角色分流）|
| /detection | 5.1kB | 检测中心 | /api/v1/context/query | 骨架就绪（演示面板硬编码）|
| /detection/result | 5.4kB | 检测中心 | /api/v1/context/company/{id} + /api/v1/decision/company/{id} | 可演示 |
| /certification | 2.3kB | 认证中心 | /api/v1/certification/levels | 骨架就绪 |
| /certification/apply | 2.0kB | 认证中心 | /api/v1/certification/apply | 骨架就绪 |
| /certification/passport/[id] | 2.5kB | 认证中心 | /api/v1/certification/status/{id} | 骨架就绪 |
| /navigation | 2.8kB | 产业导航 | — | 骨架就绪（静态5地图）|
| /assets | 2.0kB | 数据资产 | — | 骨架就绪（缺API数据）|
| /marketplace | 2.1kB | 交易市场 | /api/v1/marketplace/demands | 骨架就绪 |
| /admin | 2.5kB | 管理后台 | /api/v1/admin/stats | 骨架就绪 |
| /admin/config | 2.3kB | 管理后台 | /api/v1/admin/configs | 可演示 |
| /login | 675B | 通用 | /api/v1/auth/login | 骨架就绪 |
| /register | 675B | 通用 | /api/v1/auth/register | 骨架就绪 |

### A.5 YAML 配置 → 代码接入状态

| 配置文件 | 大小 | 用途 | 代码接入状态 |
|----------|:--:|------|:--:|
| config/scoring/default/geo_visibility.yaml | 175B | 可见度权重 | ❌ 未接入（硬编码在 geo_visibility.py）|
| config/scoring/default/trust_score.yaml | 156B | 信任分权重 | ❌ 未接入 |
| config/scoring/default/industry_index.yaml | 152B | 行业指数权重 | ❌ 未接入 |
| config/scoring/default/opportunity.yaml | 156B | 机会分权重 | ❌ 未接入 |
| config/scoring/default/visibility.yaml | 292B | 可见度参数 | ❌ 未接入 |
| config/scoring/default/assessment.yaml | 510B | 评估模型配置 | ❌ 未接入 |
| config/certification/levels.yaml | 3.6kB | 认证等级 | ✅ 已接入（certification.py 读取）|
| config/certification/review.yaml | 1.0kB | 审核规则 | ⚠️ 部分接入 |
| config/pricing/plans.yaml | 4.5kB | 套餐定义 | ⚠️ 模型已定义但未接入代码 |
| config/pricing/permissions.yaml | 2.0kB | 权限矩阵 | ⚠️ 同上 |
| config/pricing/payment.yaml | 802B | 支付规则 | ❌ 未接入（远期）|
| config/marketplace/categories.yaml | 1.8kB | 交易分类 | ⚠️ 部分接入 |
| config/competitive/intelligence.yaml | 2.6kB | 情报权重 | ❌ 未接入 |
| config/analytics/events.yaml | 2.5kB | 事件定义 | ✅ 已接入（analytics.py 读取）|

### A.6 数据库状态

| 项目 | 状态 |
|------|:--:|
| Migration 文件 | database/migrations/versions/002_initial_schema.py（17 张表）|
| Migration 执行 | ❌ 未执行（需 docker-compose up postgres）|
| 种子数据脚本 | scripts/seed_data.py（存在但未执行）|
| Docker Compose | infrastructure/docker-compose.yml（PostgreSQL + Redis）|

---

## 附录B：架构差异矩阵（设计 vs 实现）

| 系统 | 前端 | API | 引擎 | 模型 | 配置 | 闭环状态 | 关键缺口 |
|------|:--:|:--:|:--:|:--:|:--:|:--:|------|
| 检测中心 | ✅ 2页 | ✅ context+decision | ✅ Context+Decision Engine | ✅ Company等 | ❌ scoring未接入 | 可演示 | 首页演示面板硬编码；YAML权重未接入 |
| 认证中心 | ✅ 3页 | ✅ CRUD+levels | — | ✅ Certification | ⚠️ levels已接入 | 骨架就绪 | AI审核流程；证书展示；与Trust Score自动联动 |
| 产业导航 | ⚠️ 1页 | ✅ industries+companies | ⚠️ Context Engine | ✅ Industry+Relationship | — | 骨架就绪 | 五张地图动态化；企业详情页；9层价值链展示 |
| 数据资产 | ❌ 1页 | ⚠️ entities+evidence | — | ✅ Entity+Evidence | — | 骨架就绪 | 数据完整度评分；缺口分析引擎；补充建议 |
| 交易市场 | ⚠️ 1页 | ✅ marketplace | — | ✅ Demand+Order+Review | ⚠️ categories | 骨架就绪 | 能力匹配推荐；评价体系；订单流程 |
| 产业情报 | ❌ 无页面 | ✅ intelligence | — | ✅ Competitor | ❌ 未接入 | 仅设计 | 渗透机制数据流实现；情报YAML接入Decision Engine（不设独立前端页面） |
| Agent OS | — | ✅ agent API | ⚠️ 单Tool调用 | — | — | 骨架就绪 | 多步骤链路；Memory实现；TaskPlanner接入 |
| 开放生态 | — | ✅ MCP+API | — | — | — | 骨架就绪 | Developer Platform；GEO Protocol |

---

## 附录C：Sprint 历史与当前进度

| Sprint | 主题 | 完成内容 | Git 提交 |
|--------|------|----------|----------|
| Sprint 0.5 | 架构冻结 | 数据模型预审、配置体系建立、多租户扩展预留、API原则确认 | 3ca85f6 |
| Sprint 1 | 领域模型 | Entity/Capability/Relationship/Event/Evidence/Trust 六模型 + ORM + API基础层 | 551ee5c |
| Sprint 2 | Context Engine | Company/Industry/Capability Context + Context API + Ranking框架 | 04c2811 |
| Sprint 3 | Decision Engine | GEO Score/Trust Score + 6评分模型 + Recommendation + MCP基础 | 8b54013 |
| Sprint 4 | Agent OS | Agent Framework + 4 Agents + IntentRouter + TaskPlanner + MCP Tools | 3152d57 |
| Sprint 0.7 | 文档治理 | 编号体系稳定、索引.md、项目宪章 §开发规范、中文命名规范 | e2b56ec |

### C.1 当前进度总结

- 总 Python 文件：约 116 个（backend/ 下）
- 总前端页面：13 个（Next.js App Router，不含 Layout/API Routes）
- API 端点：57 个
- 集成测试：13 个（7 pass / 6 fail 仅因 PostgreSQL 未启动）
- 后端 Build：✅ 57 routes 零错误
- 前端 Build：✅ 15 routes 零错误
- Agent Framework：4 Agent 已注册，意图路由正常，但多步骤链路未实现
- YAML 配置：14 个文件，2 个已接入代码，6 个评分 YAML 未接入（P0）
- 数据库 Migration：已编写但未执行

### C.2 当前阶段：架构设计补全（P0 设计任务）

> ✅ 架构设计阶段 C.2 五项设计任务已于 2026-07-28 全部完成。当前进入 C.3 编码阶段准备。

| # | 设计任务 | 当前状态 | 目标产出 |
|---|---------|----------|---------|
| 1 | 五大系统前端信息架构 | ✅ 完成 | [06_前端信息架构设计.md] — 27页页面树+组件层级+数据来源 |
| 2 | 五大系统用户流程 | ✅ 完成 | [06-1_用户流程设计.md] — 7角色完整任务路径+状态跃迁 |
| 3 | YAML 配置 Schema | ✅ 完成 | [06-2_YAML配置Schema定义.md] — 14文件精确字段结构 |
| 4 | API 契约完整定义 | ✅ 完成 | [08-1_API契约补充定义.md] — 57端点+错误码+分页+映射 |
| 5 | 数据库 Migration 策略 | ✅ 完成 | [06-3_数据库Migration策略.md] — 17表Schema+版本管理+种子数据 |

### C.3 编码阶段 P0（架构设计完成后启动）

| # | 事项 | 前置条件 |
|---|------|---------|
| 1 | 6个评分 YAML 接入 Decision Engine | C.2-3 评分YAML Schema定稿 |
| 2 | Agent 多步骤链路 | C.2-4 相关API契约定稿 |
| 3 | 首页改造为飞轮+角色分流 | C.2-1 前端信息架构定稿 |

---

> 附录 A-C 反映的是 2026-07-28 时刻的真实仓库状态。每次重大 Sprint 完成后必须更新。

---

## 版本变更记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v2.0 | 2026-07-28 | 初始冻结版：18章+3附录，五大系统+技术架构层+最高原则+禁止事项 |
| v2.1 | 2026-07-28 | 增加：产业情报定位为共享能力层（非第六入口）、首页飞轮+角色分流设计、GEO数字身份贯穿式定义 |
| v2.2 | 2026-07-28 | 增加：数据质量五维度体系、Decision反馈闭环(P2)、时间维度(P2)、Agent OS进化路径、Entity多主体模型、用户生命周期模型(阶段0-6)、产业数字孪生正式术语、权限体系、多租户多视角、开放生态(API/MCP/GEO Protocol)、商业化优先级链、新功能准入四问、架构冻结点 |
| v2.3 | 2026-07-28 | GTP双层审查通过：修正版本号、补充变更记录。协议内容无结构性变化，确认v2.2的8项GPT建议已全部整合。正文冻结。 |
| v2.4 | 2026-07-28 | GTP边界审查：增加Identity Snapshot概念（非Engine）、五张地图=同一Knowledge Graph五种View、系统vs角色组织方式区分。无结构性变化，边界约束补充。 |
| v2.5 | 2026-07-28 | CTO独立审查修正：架构层数七→八、前端页数/路由数差异标注、硬编码豁免条款、产业情报渗透机制（数据流）、安全与权限架构（JWT+RBAC+数据隔离）、测试策略（分层+门禁）、部署与运维架构（环境+CI/CD方向）、术语统一为"五大产品系统"。 |
| v2.6 | 2026-07-28 | CTO第二轮深度审计修正（12项）：统一层数引用为技术架构层（去除七/八数字）、恢复v2.4变更记录、附录B产业情报冲突修正、L4认证等级定义补全、配置生命周期管理（active/experiments/deprecated）、用户生命周期与GEO身份概念区分、快速检测与完整检测边界定义、P0三任务依赖关系标注、角色进入路径改为推荐路径。 |
| v2.7 | 2026-07-28 | 阶段校准：P0从编码任务改为架构设计补全任务（C.2 五项设计 + C.3 编码预留）。第十一节同步更新为架构设计阶段执行计划。编码冻结至设计定稿。 |
| v2.8 | 2026-07-28 | C.2 架构设计补全5项全部完成：前端信息架构(27页)、用户流程(7角色)、YAML Schema(14文件)、API契约(57端点)、Migration策略(17表)。6份新设计文档产出，总计~85KB。 |
| v2.9 | 2026-07-28 | 架构补全终版：6个评分YAML从0.1-0.5KB stub补全到3.8-5.5KB生产级；25+份薄设计文档扩展到完整内容；ARCHITECTURE-FREEZE-AUDIT §评分升级到v4.0（20维度>=96，综合96.8）。附录C.2全部完成，C.3编码阶段准备就绪。 |


