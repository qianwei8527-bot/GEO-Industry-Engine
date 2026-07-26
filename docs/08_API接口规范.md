# GEO产业引擎 — API接口规范

> **前后端桥梁** — 后端按此规范提供接口，前端按此规范调用数据。
> 所有 endpoint 对应的业务对象定义详见 02_领域模型设计.md。

---

## 一、设计原则

- RESTful 风格，版本化（/api/v1/）
- JWT 认证（Bearer token）
- 统一响应格式
- 所有接口同时支持 Web 调用和 Agent Function Calling
- 分页、排序、筛选标准化

## 二、认证与鉴权

| 方式 | 说明 |
|------|------|
| 注册 | POST /api/v1/auth/register → 返回 token |
| 登录 | POST /api/v1/auth/login → 返回 token |
| 刷新 | POST /api/v1/auth/refresh |
| 鉴权 | Header: Authorization: Bearer {token} |

## 三、统一响应格式

```json
// 成功
{
  "code": 200,
  "data": { ... },
  "meta": { "page": 1, "page_size": 20, "total": 100 }
}

// 错误
{
  "code": 400,
  "error": {
    "type": "validation_error",
    "message": "邮箱格式不正确",
    "details": { "field": "email" }
  }
}
```

## 四、核心 API 列表

### 4.1 用户体系（/api/v1/users）

| 方法 | 路径 | 领域对象 | 说明 |
|------|------|---------|------|
| GET | /users/me | User | 获取当前用户 |
| PUT | /users/me | User | 更新个人信息 |
| GET | /users/{id} | User | 获取指定用户 |
| GET | /users/ | User[] | 用户列表（分页）|

### 4.2 企业体系（/api/v1/companies）

| 方法 | 路径 | 领域对象 | 说明 |
|------|------|---------|------|
| POST | /companies/ | Company | 创建企业 |
| GET | /companies/{id} | Company | 获取企业详情（含GEO评分）|
| PUT | /companies/{id} | Company | 更新企业信息 |
| GET | /companies/ | Company[] | 企业列表（分页+筛选）|
| GET | /companies/{id}/geo-score | GeoScore | 企业GEO评分详情 |
| GET | /companies/{id}/geo-score/history | GeoScore[] | 评分历史（三线数据源）|
| GET | /companies/{id}/visibility | Visibility[] | AI可见度数据 |

### 4.3 行业体系（/api/v1/industries）

| 方法 | 路径 | 领域对象 | 说明 |
|------|------|---------|------|
| GET | /industries/{id} | Industry | 获取行业 |
| GET | /industries/ | Industry[] | 行业列表（树形）|
| GET | /industries/{id}/sectors | Sector[] | 行业下赛道列表 |
| GET | /industries/{id}/companies | Company[] | 行业下企业列表 |
| GET | /industries/{id}/geo-index | GeoScore | 行业GEO指数 |

### 4.4 产业地图（/api/v1/maps）

| 方法 | 路径 | 领域对象 | 说明 |
|------|------|---------|------|
| GET | /maps/{type} | Map | 获取地图数据（type: ecosystem/business/operation/regional/development）|
| GET | /maps/{type}/nodes/{id} | Node | 获取地图节点详情 |
| POST | /maps/{type}/nodes | Node | 新增节点（用户提交）|
| PUT | /maps/{type}/nodes/{id} | Node | 编辑节点 |
| GET | /maps/{type}/predictions | Prediction | 地图三线预测数据 |

### 4.5 交易市场（/api/v1/marketplace）

| 方法 | 路径 | 领域对象 | 说明 |
|------|------|---------|------|
| POST | /marketplace/requests | Opportunity | 发布需求 |
| GET | /marketplace/requests | Opportunity[] | 需求列表 |
| GET | /marketplace/providers | Company[] | 服务商列表 |
| POST | /marketplace/transactions | Transaction | 创建交易 |
| GET | /marketplace/transactions/{id} | Transaction | 交易详情 |

### 4.6 认证体系（/api/v1/certification）

| 方法 | 路径 | 领域对象 | 说明 |
|------|------|---------|------|
| POST | /certification/apply | Certification | 提交认证申请 |
| GET | /certification/status | Certification | 认证状态查询 |
| POST | /certification/review | Certification | 审核操作 |
| POST | /certification/vote | Vote | 社区投票 |
| GET | /certification/scores | Certification | 三维评分详情 |

### 4.7 对标与ROI（/api/v1/benchmark）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /benchmark/compare | 多企业AI可见度对比 |
| GET | /benchmark/industry | 跨行业指数对比 |
| GET | /benchmark/roi | ROI计算 |
| GET | /benchmark/maturity | 企业GEO成熟度评估 |

### 4.8 数据查询（/api/v1/data）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /data/geo-index | GEO综合指数 |
| GET | /data/trends | 趋势数据（+预测）|
| GET | /data/reports | 研究报告列表 |
| GET | /data/reports/{id} | 研究报告详情 |
| GET | /data/knowledge-graph | 知识图谱数据 |

### 4.9 API数据服务（/api/v1/data-api）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /data-api/keys | 创建API密钥 |
| GET | /data-api/keys | 密钥列表 |
| GET | /data-api/usage | 调用量统计 |

### 4.10 Agent（/api/v1/agents）

### 4.11 AI模型智能库（/api/v1/ai-models）

#### 用户画像接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /ai-models/{id}/personas | 指定模型的用户画像列表 |
| PUT | /ai-models/{id}/personas | 更新用户画像数据 |
| GET | /ai-models/personas/comparison | 多模型用户画像对比 |

#### Prompt知识库接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /prompt-knowledge-base/ | 查询样本列表（支持按模型/行业/时间筛选）|
| GET | /prompt-knowledge-base/{id} | 查询样本详情（含完整回答+引用+提及企业）|
| POST | /prompt-knowledge-base/ | 手动新增查询样本 |
| GET | /prompt-knowledge-base/trends | 趋势分析（谁在上升/谁在下降）|
| POST | /prompt-knowledge-base/trigger-query | 手动触发向指定模型的查询并存入知识库 |

#### 品牌排名接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /brand-ranking/ | 品牌排名总榜（支持按行业/地域筛选）|
| GET | /brand-ranking/{company_id} | 指定企业的品牌排名详情（含各模型评分）|
| GET | /brand-ranking/industry/{industry_id} | 行业内的企业排名 |
| GET | /brand-ranking/trends | 排名变化趋势（上升最快/下降最快）|
| POST | /brand-ranking/refresh | 手动触发排名刷新计算

#### 查询接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /ai-models/ | 模型列表（支持筛选：type/country/status/access_type）|
| GET | /ai-models/{id} | 模型详情（含画像、指标、行为模式、行业热度）|
| GET | /ai-models/{id}/metrics | 模型指标数据 |
| GET | /ai-models/{id}/industry-scores | 模型-行业热度矩阵 |
| GET | /ai-models/{id}/behavior | 模型行为模式详情 |
| GET | /ai-models/{id}/sources | 模型来源偏好分布 |
| GET | /ai-models/{id}/query-results | 该模型的查询结果列表 |
| GET | /ai-models/comparison | 多模型对比（行业/来源/行为）|
| GET | /ai-models/ranking | 模型排名（按行业/地域/类型）|
| GET | /ai-models/query-results | 全部查询结果样本列表 |

#### 管理接口（手动操作）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /ai-models/ | 手动新增模型 |
| PUT | /ai-models/{id} | 编辑模型信息 |
| DELETE | /ai-models/{id} | 删除模型 |
| PUT | /ai-models/{id}/metrics | 手动录入/修正指标数据 |
| PUT | /ai-models/{id}/industry-scores | 调整特定行业的推荐热度 |
| PUT | /ai-models/{id}/behavior | 修正行为模式 |
| PUT | /ai-models/{id}/sources | 设置来源偏好权重 |
| POST | /ai-models/query | 手动触发向指定模型的查询 |

#### 管道管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /ai-models/pipeline/status | 数据管道运行状态 |
| POST | /ai-models/pipeline/trigger | 手动触发管道执行 |
| GET | /ai-models/pipeline/logs | 管道执行日志 |


| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /agents/ | Agent列表及状态 |
| POST | /agents/{name}/execute | 执行Agent任务 |
| GET | /agents/{name}/tasks | Agent任务历史 |
| GET | /agents/tools | 可用工具列表 |

## 五、Agent Function Calling 规范

```json
// Agent 调用示例：Industry Agent 分析行业
{
  "tool": "analyze_industry",
  "parameters": {
    "industry_id": "uuid",
    "analysis_type": "trend | opportunity | risk",
    "include_predictions": true
  }
}

// 返回
{
  "industry": { ... },
  "trends": { "historical": [...], "prediction": [...], "confidence": 0.85 },
  "opportunities": [...],
  "risks": [...]
}
```

| Agent | 可调用工具 |
|-------|-----------|
| CEO Agent | get_all_agents_status, assign_task, get_system_health |
| Industry Agent | analyze_industry, get_industry_map, get_sector_data |
| Scanner Agent | scan_ai_platform, get_geo_score, track_visibility |
| Content Agent | generate_report, optimize_content |
| Data Agent | query_knowledge_graph, aggregate_data, generate_data_report |
| Market Agent | match_demand_supply, recommend_providers |

## 六、错误码

| 范围 | 含义 |
|------|------|
| 400-499 | 客户端错误 |
| 500-599 | 服务端错误 |
| 1001-1100 | 认证相关（token过期/无效/权限不足）|
| 2001-2100 | 企业相关（不存在/已注册/验证失败）|
| 3001-3100 | 行业相关（分类不存在/层级错误）|
| 4001-4100 | 交易相关（余额不足/状态冲突）|
| 5001-5100 | 认证相关（材料不全/评分不足/审核拒绝）|

---

## 七、关联文档

| 引用的文档 | 说明 |
|-----------|------|
| 02_领域模型设计.md | 定义本文件所有 API 对应的业务对象 |
| 06_前端设计.md | 本文件为前端提供数据调用方式 |
| 07_后端设计.md | 本文件对应后端服务模块的接口暴露 |
| 05_Agent_OS设计.md | 本文件定义 Agent 可调用的工具 |
| 05_技术架构.md | 技术栈实现方案 |

> **本文件若修改，必须同步检查：02_领域模型设计.md（对象一致性）、06_前端设计.md（调用方）、07_后端设计.md（实现方）**
