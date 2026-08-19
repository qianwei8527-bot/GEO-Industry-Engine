# 恒域世界-GEO · 行业启动中心主页 Codex直接执行任务书 V10.4
> **历史/实现记录（2026-08-11 归档标注）**：本文档为恒域世界 V10.6 之前的演进记录，仅用于理解历史设计与已实现能力；发生冲突时以 V10.6 上位架构为准（docs/恒域世界_V10.6_四阶段演进架构总纲_含参考平台.md、docs/17-2_恒域世界_V10.6_整体重构_细节设计方案.md）。

> 任务编号：`V10.4-FE-HOME-EXEC-01`  
> 执行对象：ChatGPT Codex  
> 执行性质：在现有 GEO-Industry-Engine 仓库中实现前端主页  
> 页面类型：登录后的域主工作台主页，不是公开官网  
> 视觉基准：下方参考图  
> 产品基准：《恒域世界-GEO · 域主经营工作台 V10.4》  
> 当前授权：只实现本主页及必需的共享界面壳，不扩展其他页面  
> 日期：2026-08-04

---

# 0. 给Codex的总指令

你现在不是输出设计建议，而是在现有 `GEO-Industry-Engine` 仓库中完成“恒域世界-GEO · 行业启动中心主页”的前端实现。

必须先只读审计仓库，再实施、测试和验收。优先复用现有路由、认证、Realm权限、组件、图谱、Evidence、Demand、Connection和Agent基础设施。不得为了还原图片而创建第二套业务真相源，不得使用虚构业务数据填满界面。

最终必须交付可运行页面、测试、截图、修改清单、复用清单、未接通能力和真实输入阻塞报告。不要只提交一份分析报告。

---

# 1. 参考图

![恒域世界-GEO行业启动中心主页](./generated_images/恒域世界-GEO_主页设计_V10.4.png)

参考图原始尺寸：`1586 × 992`。

参考图负责定义：

- 整体视觉方向；
- 页面层级；
- 模块位置；
- 主要文案；
- 空状态；
- 控件密度；
- 色彩关系。

如果参考图与现有V10真实性、权限或数据协议冲突，以真实性、权限和现有协议为准，并在验收报告中说明差异。

---

# 2. 最终页面目标

实现一个帮助陌生行业初创域主启动业务的首页，完成以下闭环：

```text
补齐真实输入
→ 建立行业认知
→ 查看行业业务流程
→ 确认自己的位置
→ 发布资源需求
→ 获得带证据的匹配
→ 建立真实连接
→ 确定首个试点
→ 解锁90天计划
```

本页不是传统数据看板，不以数字卡片和图表作为核心；地图、任务、资源连接和下一步行动才是核心。

---

# 3. 执行范围

## 3.1 必须完成

- 域主工作台共享页面壳；
- 左侧六个一级工作面；
- 顶部Realm经营语境条；
- 行业启动中心标题区；
- 四项真实状态条；
- 本周启动任务；
- 行业演化与资源地图主画布；
- 业务流程、需求方案、资源地图切换；
- “我的位置：待确认”；
- 优先资源与连接；
- 可信信息流；
- 下一步行动；
- truth scope图例；
- AI域主助手和决策审批入口；
- 加载、空、阻塞、部分数据、错误和权限状态；
- 响应式基础支持；
- 类型、测试、构建和视觉截图。

## 3.2 本任务禁止扩展

- 不完整开发经营、增长、交付、复制和资产页面；
- 不新增支付、订单、会员和财务系统；
- 不开发新的公共行业门户；
- 不开发完整CRM；
- 不自动联系客户、专家、渠道或合作伙伴；
- 不新增数据抓取平台；
- 不批量生成行业节点；
- 不新增数据库模型或Alembic迁移，除非另行获得域主明确批准；
- 不重做现有V10权限、证据、信誉和连接状态机。

---

# 4. 开始前的强制只读审计

Codex在修改任何文件前必须完成：

1. 读取仓库根目录及子目录中的 `AGENTS.md`；
2. 执行 `git status --short`，识别并保护用户已有修改；
3. 使用 `rg --files` 找到前端目录、路由目录、组件目录和测试目录；
4. 查找现有 `/realm`、`/universe`、`/company` 页面；
5. 查找现有 Layout、Sidebar、Header、Breadcrumb、Drawer、Tabs、Button、EmptyState、Skeleton、Graph/Canvas 组件；
6. 查找现有认证、当前用户、Realm、Membership和权限数据流；
7. 查找现有 Evidence、EvidenceClaim、World Projection、Demand Event、Connection Candidate、Engagement、SOP Run和Agent Run接口；
8. 查找现有主题变量、字体、图标库和响应式规则；
9. 查找项目实际使用的包管理器和测试命令；
10. 输出一份简短的“复用清单 + 缺口清单 + 预计修改文件”，然后立即继续执行。

只读审计阶段禁止：

- 创建新数据库表；
- 安装新的UI框架；
- 替换现有认证；
- 删除旧页面；
- 覆盖用户未提交修改。

---

# 5. 路由要求

优先路由：

```text
/realm/{realm_id}/explore
```

如果现有项目的Realm路由协议不同：

- 使用现有协议建立等价页面；
- 不为匹配本任务书再建立第二套路由体系；
- 在交付报告中写明最终路由和原因。

访问规则：

- 未登录：进入现有登录流程；
- 已登录但不是Realm成员：返回现有403或无权状态；
- 是Realm成员但无管理权限：允许读取公开/授权数据，隐藏高风险操作；
- 域主/owner：显示全部已授权操作；
- 不得由前端自行判断owner身份，必须使用现有权限真相源。

---

# 6. 页面精确拆解

## 6.1 全局结构

```text
RealmOwnerLayout
├── PrimarySidebar
├── RealmContextHeader
└── ExploreHomePage
    ├── PageHeading
    ├── StartupTruthStrip
    ├── MainWorkspaceGrid
    │   ├── StartupTaskRail
    │   ├── IndustryEvolutionCanvas
    │   └── ResourceConnectionPanel
    ├── BottomWorkspaceGrid
    │   ├── TrustedInformationFeed
    │   └── NextBestActionPanel
    ├── TruthScopeLegend
    ├── RealmAIAssistantDrawer
    └── DecisionApprovalDrawer
```

## 6.2 布局尺寸

基准视口：`1440 × 900`，同时用参考图尺寸 `1586 × 992` 做视觉回归。

| 区域 | 目标规格 |
| --- | --- |
| 左侧导航 | 176—192px固定宽度 |
| 顶部栏 | 64—68px高度 |
| 主内容外边距 | 24—28px |
| 页面标题区 | 约84—96px |
| 状态条 | 60—64px |
| 主工作区 | 左220px / 中自适应 / 右280px |
| 主工作区最小高度 | 400px |
| 底部工作区 | 左约48% / 右约52% |
| 模块间距 | 12—16px |
| 圆角 | 10—12px |
| 边框 | 1px浅灰 |

要求：

- 地图必须是首屏最大区域；
- 1440 × 900下不得出现横向滚动；
- 关键主按钮、地图和下一步行动首屏可见；
- 页面可以纵向滚动，但不能把核心行动藏在多屏之后。

---

# 7. 固定文案

除非域主配置覆盖，否则首期使用以下文案。

## 7.1 品牌与导航

```text
恒域世界-GEO
探索
经营
增长
交付
复制
资产
```

导航顺序不能改变，“探索”为当前激活项。

## 7.2 顶部语境

```text
恒域世界-GEO / GEO服务域 / 行业验证期 / 90天待解锁
AI域主助手
决策与审批
```

## 7.3 页面标题

```text
行业启动中心
从认识行业，到建立首个有效连接
```

## 7.4 真实状态条

```text
真实输入：待补齐
行业认知：未建立
资源需求：未发布
有效连接：无记录
```

## 7.5 启动任务

```text
本周启动任务
1 明确行业与赛道
2 确认首个试点关系
3 定义标准GEO产品
4 发布首个资源需求
开始补齐真实输入
```

## 7.6 地图

```text
行业演化与资源地图
业务流程
需求方案
资源地图
拉取配置
需求出现
诊断决策
解决方案
生产交付
分发触达
反馈评估
我的位置：待确认
```

## 7.7 资源与连接

```text
优先资源与连接
行业专家
渠道资源
交付伙伴
先发布真实需求，系统再提供带证据的匹配
发布资源需求
```

## 7.8 可信信息流

```text
可信信息流
官方规则
行业研究
用户需求
案例方法
暂无信息
选择上方来源类型，获取可信内容
```

## 7.9 下一步行动与图例

```text
下一步行动
确定首个真实试点与品牌关系
完成后解锁90天计划
已验证
已观察
AI推断
预演
```

不得使用Lorem Ipsum，不得在生产页面写“示例公司A”“客户12家”等虚构内容。

---

# 8. 组件实现任务

组件名是逻辑建议。若仓库已有命名规范，遵循仓库规范，但职责不得丢失。

## 8.1 `PrimarySidebar`

必须实现：

- 品牌标识和“恒域世界-GEO”；
- 六个一级导航；
- 探索激活态；
- 图标和文字；
- 键盘焦点；
- 窄屏折叠；
- 权限不改变一级导航名称，只改变进入后的状态或操作能力。

禁止：

- 增加“仪表盘”“首页”等重复项；
- 使用emoji作为正式图标；
- 为实现页面再安装一套大型图标库；
- 用隐藏导航代替权限提示。

## 8.2 `RealmContextHeader`

必须实现：

- Realm路径语境；
- 搜索入口；
- AI域主助手入口；
- 决策与审批入口；
- 语境内容来自真实Realm和经营阶段；
- 无数据时显示“待确认”或“待解锁”，不猜测。

## 8.3 `StartupTruthStrip`

四个状态项等宽排列，不做大数字卡片。

状态来源：

| 状态项 | 计算依据 |
| --- | --- |
| 真实输入 | 试点品牌、主体、关系、产品、客户、地区、问题、渠道、转化目标等输入完整度 |
| 行业认知 | 行业基线或研究问题是否存在及其证据状态 |
| 资源需求 | 是否存在当前Realm的有效Demand Event / ResourceNeed |
| 有效连接 | 是否存在qualified、accepted或completed连接记录 |

前端不能仅凭列表长度判断“已验证”。

## 8.4 `StartupTaskRail`

任务状态：

```ts
type StartupTaskStatus =
  | "locked"
  | "ready"
  | "in_progress"
  | "blocked"
  | "needs_review"
  | "completed";
```

交互：

- 点击任务打开侧边抽屉；
- 点击主按钮打开真实输入分步表单；
- 任务完成必须有后端对象、审批记录或真实Evidence；
- 只完成前端表单不能直接变成`completed`；
- 显示当前步骤、阻塞原因和下一步。

## 8.5 `IndustryEvolutionCanvas`

首期绘制六个基础域点：

```text
需求出现 → 诊断决策 → 解决方案 → 生产交付 → 分发触达 → 反馈评估
```

必须实现：

- 横向流程连接；
- 六个圆形或接近圆形节点；
- 节点图标、标题和状态边框；
- 指向“我的位置”的虚线关系；
- “我的位置：待确认”占位节点；
- 三个视图切换；
- 拉取配置；
- 节点点击和详情抽屉；
- 缩放、平移、重置；
- 键盘可达的节点列表替代入口；
- truth scope样式。

数据规则：

- 优先消费现有World Projection和State Snapshot；
- 没有World数据时渲染“流程模板”，必须标记为配置模板或预演；
- 不能把流程模板写回真实World；
- 拖拉或组合只形成draft/simulation；
- verified、observed、inferred、simulation必须可区分。

性能：

- 首页只加载当前六节点和必要关系；
- 不在首页加载完整产业图谱；
- 地图错误只影响地图模块；
- 首屏后再懒加载节点详情。

## 8.6 `ResourceConnectionPanel`

空状态只展示三类资源及占位，不生成候选名称。

点击“发布资源需求”打开表单：

```text
业务目标
所在流程环节
缺少的能力或资源
服务地区
时间要求
预算范围
合作方式
必须条件
排除条件
允许共享的数据范围
```

有真实匹配后，每个候选显示：

- 真实主体名称；
- 资源类型；
- 可以解决的需求；
- 匹配理由；
- Evidence或来源；
- truth status；
- 风险和未知项；
- 连接状态；
- 下一步操作。

连接状态必须复用：

```text
proposed → qualified → accepted → completed
                     ↘ rejected
```

AI可以起草联系内容，但未经域主确认不能发送。

## 8.7 `TrustedInformationFeed`

四个筛选项：

- 官方规则；
- 行业研究；
- 用户需求；
- 案例方法。

信息项必须包含：

- 标题；
- 来源；
- 记录时间；
- 适用范围；
- 原文/摘要/推断类型；
- truth status；
- 证据引用；
- 查看详情。

空状态显示引导，不使用假文章。

## 8.8 `NextBestActionPanel`

默认行动：

```text
确定首个真实试点与品牌关系
完成后解锁90天计划
```

下一步行动必须由阶段门和真实数据决定，显示：

- 行动名称；
- 为什么现在做；
- 所需输入；
- 完成标准；
- 点击目标；
- 阻塞原因。

AI只能提出候选行动，不能自行将阶段门标记为通过。

## 8.9 `TruthScopeLegend`

```ts
type TruthScope = "verified" | "observed" | "inferred" | "simulation";
```

中文映射：

| 状态 | 文案 | 含义 |
| --- | --- | --- |
| verified | 已验证 | 满足证据和验证规则 |
| observed | 已观察 | 有真实记录但未完成验证 |
| inferred | AI推断 | AI根据已知事实提出的推断 |
| simulation | 预演 | 仅用于配置和未来分析 |

不能只用颜色表达，必须同时使用文字或图形差异。

---

# 9. 建议前端ViewModel

不要直接让页面拼装多个松散API响应。优先建立只负责展示转换的类型化adapter。

```ts
type TruthScope = "verified" | "observed" | "inferred" | "simulation";

type ReadinessStatus =
  | "unknown"
  | "missing"
  | "partial"
  | "ready"
  | "blocked"
  | "stale";

interface RealmOwnerHomeViewModel {
  realm: {
    id: string;
    displayName: string;
    worldName: string | null;
    trackName: string | null;
    businessStage: string | null;
    operatingCycleLabel: string | null;
    permissions: string[];
  };
  readiness: {
    realInputs: ReadinessStatus;
    industryKnowledge: ReadinessStatus;
    resourceDemand: ReadinessStatus;
    validConnections: ReadinessStatus;
  };
  startupTasks: Array<{
    id: string;
    title: string;
    status: StartupTaskStatus;
    blockedReason: string | null;
    targetHref: string | null;
  }>;
  map: {
    mode: "business_flow" | "demand_solution" | "resource_map";
    nodes: Array<{
      id: string;
      label: string;
      truthScope: TruthScope;
      isTemplate: boolean;
    }>;
    edges: Array<{
      id: string;
      source: string;
      target: string;
      truthScope: TruthScope;
    }>;
    ownerPosition: {
      status: "unknown" | "draft" | "confirmed";
      nodeIds: string[];
    };
  };
  resources: {
    hasDemand: boolean;
    groups: Array<{
      type: "expert" | "channel" | "delivery_partner";
      candidates: Array<{
        id: string;
        name: string;
        reason: string;
        truthScope: TruthScope;
        risk: string | null;
        unknowns: string[];
        connectionStatus: string;
      }>;
    }>;
  };
  information: Array<{
    id: string;
    category: "official" | "research" | "user_need" | "case_method";
    title: string;
    sourceName: string;
    observedAt: string | null;
    truthScope: TruthScope;
  }>;
  nextAction: {
    title: string;
    reason: string;
    completionCondition: string;
    targetHref: string | null;
    blockedReasons: string[];
  };
}
```

约束：

- `unknown`不能转换为0；
- `null`不能被前端文案伪装成“正常”；
- adapter只转换展示格式，不复制权限、验证和信誉规则；
- 所有查询必须包含真实realm_id和scope；
- 跨Realm切换后必须清理旧缓存。

---

# 10. 真实数据复用要求

| 页面能力 | 必须优先检查和复用 |
| --- | --- |
| 当前Realm | entities、realm_registry |
| 当前成员和owner权限 | node_memberships |
| 行业地图 | World Projection、World State Snapshot |
| 行业信息和真相状态 | Evidence、EvidenceClaim、Binding |
| 资源需求 | Demand Event；现有表达不足时只报告缺口 |
| 匹配候选 | Connection Candidate |
| 真实协作 | Engagement |
| 项目 | GEO Project、Work Item |
| 90天运行 | SOPTemplate、SOPRun、StepRun；没有则先用阻塞状态 |
| AI运行 | Agent Run、Tool Execution、Memory、Citation |
| 结果 | Outcome；前端不得直接修改Reputation |

如果某项API不存在：

1. 不创建静态生产JSON；
2. 不编造正式接口；
3. 实现类型边界和真实空状态；
4. 将缺失API写入交付报告；
5. 未经批准不新增数据库迁移。

---

# 11. 交互流程

## 11.1 补齐真实输入

```text
点击“开始补齐真实输入”
→ 打开分步抽屉
→ 填写真实试点资料或选择“不知道”
→ 前端校验
→ 调用现有真实接口
→ 保存成功后重新拉取ViewModel
→ 更新状态条和启动任务
```

“不知道”必须生成缺口或研究任务，不能由AI自动填写为事实。

## 11.2 地图切换

```text
点击业务流程 / 需求方案 / 资源地图
→ 只更新地图视图状态
→ 按需请求对应投影
→ 保留当前Realm和truth scope
→ 请求失败显示地图模块错误
```

## 11.3 确认我的位置

```text
点击“我的位置：待确认”
→ 打开位置配置抽屉
→ 选择当前能力域点
→ 绑定企业、品牌、产品或团队
→ 添加来源或Evidence
→ 保存为draft/observed
→ 审核后才允许confirmed
```

## 11.4 发布资源需求

```text
填写结构化需求
→ AI可整理草稿
→ 域主确认
→ 创建现有Demand对象
→ 获取Connection Candidate
→ 展示理由、证据、风险和未知项
→ 域主确认是否接洽
```

## 11.5 解锁90天计划

至少满足：

- 首个试点品牌真实明确；
- 品牌关系明确；
- 核心产品明确；
- 目标客户明确；
- 主要转化目标明确；
- 标准GEO产品可以说明。

未满足时必须显示缺口，不允许前端直接解锁。

---

# 12. 页面状态

所有模块必须支持：

| 状态 | 处理 |
| --- | --- |
| loading | 使用与最终结构一致的骨架，避免布局跳动 |
| empty | 说明为空的原因和下一步 |
| blocked | 显示阻塞条件和解锁入口 |
| partial | 保留已有真实数据，单独标记缺失项 |
| error | 模块级错误、重试和错误引用 |
| forbidden | 不暴露资源是否存在，只显示权限不足 |
| stale | 显示过期时间和重新核验入口 |
| ready | 展示来源、状态和更新时间 |

任一子模块失败不得导致整页白屏。

---

# 13. 视觉实现规范

## 13.1 设计变量

如果仓库已有主题系统，将以下值映射到现有变量；不要并行建立第二套主题系统。

```css
--realm-page-bg: #f7f9f8;
--realm-surface: #ffffff;
--realm-text-primary: #101828;
--realm-text-secondary: #667085;
--realm-border: #dde3e7;
--realm-primary: #006c68;
--realm-primary-hover: #005a57;
--realm-action: #0b63e6;
--realm-ai: #6c4cf6;
--realm-radius: 12px;
```

## 13.2 字体

- 页面标题：28—32px，700；
- 模块标题：16—18px，600；
- 正文：14px；
- 辅助文字：12px；
- 中文优先使用项目现有无衬线字体；
- 不为此页单独加载体积过大的字体包。

## 13.3 禁止样式

- KPI卡片墙；
- 大面积渐变；
- 玻璃拟态；
- 霓虹科技感；
- 3D地球；
- 人物或图库照片；
- 重阴影；
- 多个同权重主色；
- 只有图标没有可访问名称的关键按钮；
- 低对比度浅灰正文。

---

# 14. 响应式与可访问性

## 14.1 响应式

| 宽度 | 行为 |
| --- | --- |
| ≥1280px | 三列主工作区，完整侧栏 |
| 1024—1279px | 收窄侧栏，资源连接进入抽屉，地图保持主区 |
| 768—1023px | 主工作区改为单列或两列，地图优先 |
| <768px | 保证阅读、任务和发布需求；完整地图编辑可降级为列表 |

不得简单缩放桌面截图。

## 14.2 可访问性

- 所有关键交互可用键盘；
- 焦点状态明显；
- 颜色对比达到WCAG AA；
- 状态不能只依赖颜色；
- 图标按钮有`aria-label`；
- Tabs使用正确语义；
- 地图提供列表等价入口；
- 尊重`prefers-reduced-motion`；
- 125%浏览器缩放时不遮挡关键按钮。

---

# 15. 工程约束

- 使用现有Next.js和TypeScript架构；
- 使用现有样式系统和组件库；
- 如果项目已有图标库，必须复用；
- 如果项目已有图组件，优先复用；
- 不为一个页面安装大型UI或图谱框架；
- 不修改后端权限真相；
- 不在前端保存API Key；
- 不使用`any`绕过核心数据类型；
- 不隐藏构建、lint、测试或控制台错误；
- 不删除现有页面和路由；
- 不覆盖用户已有修改；
- 不提交或推送Git，除非用户另行明确要求；
- 开发fixture只能存在于测试环境，不能进入生产数据路径。

---

# 16. 文件组织建议

Codex必须先适配仓库实际目录。以下只表示逻辑结构：

```text
frontend/
├── app-or-pages/
│   └── realm/[realm_id]/explore/page.tsx
├── components/
│   └── realm-owner/
│       ├── realm-owner-shell.tsx
│       ├── primary-sidebar.tsx
│       ├── realm-context-header.tsx
│       ├── startup-truth-strip.tsx
│       ├── startup-task-rail.tsx
│       ├── industry-evolution-canvas.tsx
│       ├── resource-connection-panel.tsx
│       ├── trusted-information-feed.tsx
│       ├── next-best-action-panel.tsx
│       ├── truth-scope-legend.tsx
│       └── realm-ai-assistant-drawer.tsx
├── lib/
│   └── realm-owner-home/
│       ├── types.ts
│       ├── adapter.ts
│       ├── config.ts
│       └── queries.ts
└── tests/
    └── realm-owner-home/
```

如果已有同类组件，扩展现有文件，不机械复制上述目录。

---

# 17. Codex执行阶段

## Phase A：审计与复用

- 完成第4节全部检查；
- 输出复用组件和真实API清单；
- 确定最终路由和文件；
- 记录后端缺口；
- 不等待用户回复，安全范围内继续前端实现。

## Phase B：共享页面壳

- 实现或复用Realm Owner Layout；
- 完成六导航；
- 完成顶部语境；
- 接入认证和Realm权限；
- 确保不破坏旧页面。

## Phase C：真实空状态主页

- 实现所有模块和固定文案；
- 实现参考图布局；
- 实现loading、empty、blocked、error；
- 不接假数据；
- 生成首次视觉截图。

## Phase D：接入现有真实数据

- Realm和Membership；
- World Projection；
- Evidence和Claim；
- Demand Event；
- Connection Candidate和Engagement；
- 现有SOP/Agent状态；
- 只接已存在且权限明确的接口。

## Phase E：交互

- 真实输入抽屉；
- 地图视图切换；
- 节点详情；
- 我的位置信息草稿；
- 资源需求表单；
- AI草稿与人工确认；
- 下一步行动。

## Phase F：测试和收口

- 格式化；
- TypeScript检查；
- lint；
- 单元和组件测试；
- E2E；
- 生产构建；
- 1440 × 900及1586 × 992截图；
- 无障碍和性能检查；
- 输出验收报告。

---

# 18. 测试要求

## 18.1 单元测试

至少覆盖：

- truth scope映射；
- readiness状态计算；
- 阶段门计算；
- 下一步行动选择；
- ResourceNeed表单校验；
- Realm切换清理缓存；
- `unknown`不被转换为0或成功。

## 18.2 组件测试

至少覆盖：

- 六导航和探索激活态；
- 状态条空状态；
- 启动任务状态；
- 地图三个Tabs；
- 我的位置信息入口；
- 资源需求空状态和表单；
- 可信信息筛选；
- AI高风险动作确认；
- 单模块错误不影响整页。

## 18.3 E2E场景

```text
场景1：未登录访问
场景2：非Realm成员访问
场景3：域主在blocked_by_real_inputs状态进入主页
场景4：补齐部分真实输入
场景5：切换三个地图视图
场景6：发布资源需求
场景7：已有候选时查看理由、证据、风险和未知项
场景8：打开AI助手但不允许自动发送
场景9：地图API失败，其他模块仍可用
场景10：Realm切换后旧数据不残留
```

测试命令必须使用仓库现有包管理器。不要在未审计的情况下假定npm、pnpm、yarn或bun。

---

# 19. 验收标准

## 19.1 页面结构

- [ ] 页面可从最终Realm路由访问；
- [ ] 六个一级导航名称与顺序完全正确；
- [ ] 探索有清晰激活态；
- [ ] 顶部语境、AI助手和决策审批入口存在；
- [ ] 地图是首屏最大模块；
- [ ] 任务、资源、信息和下一步行动位置与参考图一致；
- [ ] 无重复首页或仪表盘入口。

## 19.2 文案与空状态

- [ ] 页面标题和副标题完全正确；
- [ ] 四项状态显示待补齐、未建立、未发布、无记录；
- [ ] 四项启动任务顺序正确；
- [ ] 六个业务流程节点顺序正确；
- [ ] 无虚构公司、客户、收入、案例、百分比和候选资源；
- [ ] 每个空状态都有下一步入口。

## 19.3 地图

- [ ] 三个地图视图可以切换；
- [ ] 节点可以点击并查看基础信息；
- [ ] 支持缩放、平移和重置；
- [ ] “我的位置：待确认”可以打开配置；
- [ ] truth scope可以区分；
- [ ] 模板和预演不会写成生产事实；
- [ ] 首页不加载完整产业图谱。

## 19.4 资源连接

- [ ] 无需求时不生成候选；
- [ ] ResourceNeed必须包含目标和能力缺口；
- [ ] 候选显示理由、证据、风险和未知项；
- [ ] 连接状态复用现有状态机；
- [ ] AI不能自动发送；
- [ ] 域主确认后才能进入真实连接。

## 19.5 真实性与权限

- [ ] observed不显示为verified；
- [ ] inferred和simulation有明确标识；
- [ ] 前端不能修改Reputation；
- [ ] 权限使用node_memberships或现有唯一真相源；
- [ ] 跨Realm数据不串用；
- [ ] 缺少API时显示真实缺口，不使用生产mock。

## 19.6 视觉

- [ ] 1440 × 900无横向滚动；
- [ ] 主体结构相对参考图重大偏差不超过约5%；
- [ ] 中文无乱码、遮挡和异常换行；
- [ ] 没有KPI卡片墙、霓虹、3D地球、图库照片和重阴影；
- [ ] 125%缩放可用；
- [ ] 响应式降级符合第14节。

## 19.7 工程质量

- [ ] 类型检查通过；
- [ ] lint通过；
- [ ] 相关测试通过；
- [ ] 生产构建通过；
- [ ] 控制台无错误；
- [ ] 无未处理Promise；
- [ ] 无新增数据库迁移；
- [ ] 无真实API Key和敏感数据进入仓库；
- [ ] 保留用户已有修改。

## 19.8 性能与可访问性

- [ ] 核心内容LCP目标小于2.5秒；
- [ ] CLS目标小于0.1；
- [ ] 常规操作反馈目标小于200ms；
- [ ] 颜色对比达到WCAG AA；
- [ ] 关键操作可键盘完成；
- [ ] 地图有列表等价入口；
- [ ] 状态不只依赖颜色。

---

# 20. 完成定义

只有全部满足才可以报告完成：

1. 页面真实可运行；
2. 参考图主体结构已经实现；
3. 真实空状态完整；
4. 已有真实接口已复用；
5. 缺失接口没有用假数据替代；
6. 所有关键动作有权限和人工确认；
7. 测试与构建通过；
8. 输出桌面截图；
9. 输出修改文件清单；
10. 输出复用组件/API清单；
11. 输出未接通能力和真实输入缺口；
12. 没有新增未经批准的模型、迁移和功能范围。

---

# 21. Codex最终回报格式

Codex完成后必须按以下格式回复域主：

```md
# V10.4 行业启动中心主页执行报告

## 1. 完成结果
- 最终路由：
- 页面状态：
- 视觉还原情况：

## 2. 复用内容
- 复用组件：
- 复用API：
- 复用数据模型：

## 3. 修改文件
- 新增：
- 修改：
- 未修改但相关：

## 4. 真实数据状态
- 已接通：
- 仍为空：
- blocked_by_real_inputs：

## 5. 测试结果
- TypeScript：
- lint：
- 单元/组件：
- E2E：
- build：
- 控制台：

## 6. 验收截图
- 1440 × 900：
- 1586 × 992：

## 7. 未完成与阻塞
- 缺失API：
- 缺失真实输入：
- 需要域主决策：

## 8. 下一步建议
- 只列与本主页直接相关的下一步，不扩展到其他工作面。
```

禁止只回复“页面已完成”。

---

# 22. 可直接复制给Codex的启动口令

```text
执行仓库内《恒域世界-GEO · 行业启动中心主页 Codex直接执行任务书 V10.4》：

1. 先完成强制只读审计，保护现有修改；
2. 参考图是视觉基准，V10真实性与权限协议是业务基准；
3. 只实现行业启动中心主页和必需的共享界面壳；
4. 复用现有Realm、World、Evidence、Demand、Connection、Engagement、SOP和Agent能力；
5. 可以实现真实空状态，但不得用虚构业务数据填满页面；
6. 未经批准不新增数据库模型和迁移；
7. 完成实现、测试、构建、截图和验收报告；
8. 安全范围内自主执行，不要停留在计划或分析阶段。
```

