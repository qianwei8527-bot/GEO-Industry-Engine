# GEO产业内核与开放协议

> 正式定义GEO产业引擎的“操作系统内核”——其他系统、Agent、平台通过协议调用它。

---

## 一、产业内核（Industry Kernel）

| 引擎 | 职能 | 输入 | 输出 |
|---------|----------|---------|---------|
| Entity Engine | 实体识别、注册、跟踪 | 企业/个人/产品信息 | 统一GEO ID |
| Relationship Engine | 关系发现、计算、更新 | 实体对 | 关系类型+权重 |
| Capability Engine | 能力识别、验证、等级 | 能力描述+证据 | 能力张量(L1-L4) |
| Value Engine | 价值评估、机会匹配 | 需求+供给对 | 商业价值评分 |
| Recommendation Engine | AI推荐因子分析 | 企业+AI模型 | 推荐权重+置信度 |
| Evolution Engine | 产业演化预测 | 历史数据+趋势 | 变化预测+机会热图 |

## 二、开放协议（Open Protocol）

| 协议 | 用途 | 调用方式 |
|---------|------|-----------|
| GEO Entity Protocol | 查询、创建、更新实体 | REST API + GraphQL |
| GEO Data Protocol | 访问GEO产业数据 | REST API + WebSocket |
| GEO Certification Protocol | 验证、飘发认证 | REST API |
| GEO Agent Protocol | Agent发现、调用GEO服务 | Function Calling规范 |

## 三、内核与现有架构的关系

| 现有模块 | 对应内核引擎 |
|-------------|----------------|
| 14_实体智能与信息供应链 | Entity Engine |
| 02_领域模型设计 | Entity + Relationship Engine |
| 12_用户行为与AI决策路径 | Recommendation Engine |
| 13_产业发展趋势与职业生态 | Evolution Engine |
| 15_竞争情报与增长实验 | Value + Capability Engine |
