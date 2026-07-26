import os

content = """# 执行方案与90天计划

> 从24份文档到第一行生产代码：90天跑通核心闭环。

---

## 一、战略聚焦：90天只做一件事

**唯一目标：让B2B供应商看到自己在AI中的推荐情况。**

不做的（即使文档里写了）：
- 产业地图（5张图全部延后）
- 交易市场（延后）
- 认证体系L2+（只做L1企业实名）
- Agent OS（延后）
- Neo4j知识图谱（延后）
- 前端多页面（只有一个Dashboard）

**做的：**

```
用户注册 -> 添加企业 -> AI扫描(发送Prompt) -> GEO评分 -> 展示Dashboard -> (可选)付费订阅
```

---

## 二、团队构成

| 角色 | 人数 | 技能要求 | 核心职责 |
|------|------|---------|---------|
| 全栈工程师（后端为主） | 1人 | FastAPI, SQLAlchemy, PostgreSQL, Python | 用户系统、AI查询引擎、评分计算 |
| 全栈工程师（前端为主） | 1人 | Next.js, React, Tailwind, TypeScript | Dashboard、登录/注册页、报告展示 |
| AI/数据工程师 | 1人（可兼职） | LLM API, NLP, 爬虫 | Prompt库、查询管道、实体提取 |
| **合计** | **2-3人** | | |

---

## 三、90天周计划

### 第1-2周：基础搭建

| 任务 | 产出 | 依赖 |
|------|------|------|
| GitHub仓库+CI/CD(18号文档) | PR通过后自动运行测试 | 无 |
| Docker Compose环境(PostgreSQL+Redis) | docker compose up即可运行 | 无 |
| 数据库Schema(用户+企业+查询结果表) | Alembic迁移脚本 | 无 |
| FastAPI项目骨架(路由+中间件+异常) | /health返回200 | 无 |
| Next.js项目骨架(页面+布局+API客户端) | 空白页面可访问 | 无 |

**里程碑1(Week 2末)**：`docker compose up`后，访问localhost:8000/health返回200，访问localhost:3000看到空白页面。

### 第3-4周：用户系统 + 企业注册

| 任务 | 产出 | 依赖 |
|------|------|------|
| 用户注册/登录API | POST /auth/register, /auth/login | 数据库Schema |
| JWT认证中间件 | 受保护路由需要token | 用户API |
| 企业CRUD API | POST /companies, GET /companies/{id} | 用户系统 |
| 用户注册页面 | 注册表单+登录表单 | API |
| 企业添加页面 | 输入企业名+网址 | 用户页面 |

**里程碑2(Week 4末)**：用户可以注册、登录、添加企业。

### 第5-6周：AI查询引擎（核心攻坚）

| 任务 | 产出 | 依赖 |
|------|------|------|
| Prompt库设计(10个行业x10个查询=100个) | prompts.json | 无 |
| LLM API集成(ChatGPT+Gemini+DeepSeek) | python lib/llm_clients.py | API Key |
| 并发查询调度器 | 向3个模型并发发送10个Prompt | LLM集成 |
| 结果解析(提取回答+引用+企业名) | results/parser.py | 查询结果 |
| 查询结果入库 | INSERT INTO ai_query_results | 数据库Schema |

**关键代码示例：AI查询引擎核心**

```python
# lib/llm_clients.py - 伪代码
import asyncio
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

async def query_chatgpt(prompt: str) -> dict:
    resp = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return {
        "model": "chatgpt",
        "response": resp.choices[0].message.content,
        "usage": resp.usage.total_tokens
    }

# 并发调度器
async def batch_query(prompts: list[str]):
    tasks = [query_chatgpt(p) for p in prompts]
    return await asyncio.gather(*tasks, return_exceptions=True)
```

**里程碑3(Week 6末)**：向3个模型发送10个Prompt，结果存入数据库。

### 第7-8周：GEO评分引擎

| 任务 | 产出 | 依赖 |
|------|------|------|
| 提及频率计算 | companies/{id}/visibility | AI查询结果 |
| 排名位置提取 | 从回答中解析排名顺序 | 结果解析 |
| 情感分析 | 正面/中性/负面判断 | LLM辅助或规则 |
| 简化GEO评分(4因子) | GET /geo-score/{company_id} | 以上三项 |
| 模拟数据验证(10家企业) | 对比预期vs实际 | 评分引擎 |

**评分公式(MVP简化版)：**

```
GEO_Score = 品牌提及率 × 0.40
          + 平均排名位置 × 0.25
          + 情感倾向分 × 0.20
          + 引用深度(引用数) × 0.15
```

对比16号文档的9因子，砍掉5个理论因子(实体清晰度、空间竞争、行业相关度、模型偏好、时效性)，只保留4个可以直接从AI回答中提取的因子。

**里程碑4(Week 8末)**：输入企业ID，返回GEO评分(0-100)和置信度。

### 第9-10周：前端Dashboard

| 任务 | 产出 | 依赖 |
|------|------|------|
| Dashboard页面布局 | 评分卡片+趋势图+分析列表 | 评分API |
| GEO评分展示组件 | 企业名+评分+置信度+趋势箭头 | 评分API |
| 竞品对比组件 | 多企业并排对比 | 评分API |
| 账户管理(免费/Pro) | Stripe/Paddle支付集成 | 用户系统 |

**里程碑5(Week 10末)**：用户登录后看到企业GEO评分和竞品对比。

### 第11-12周：报告 + 发布

| 任务 | 产出 | 依赖 |
|------|------|------|
| PDF报告生成 | 下载企业GEO月报 | Dashboard |
| 邮件周报 | 每周自动发送评分变化 | 报告API |
| 定价页面 | Free/Pro功能对比+支付 | 账户管理 |
| 上线检查 | 日志+监控+错误追踪 | 全部 |

**里程碑6(Week 12末)**：产品上线，首批种子用户可注册使用。

---

## 四、关键路径

```
Week 2: Docker + 数据库            ┐
                                   │ 关键路径
Week 4: 用户 + 企业注册             │（不可并行）
                                   │
Week 6: AI查询引擎 ★★★★★ 最难      ┘
                                   ┐
Week 8: GEO评分引擎                │ 可并行
                                   │
Week 10: Dashboard + 竞品对比       │
                                   │
Week 12: 报告 + 发布               ┘
```

**风险最高的环节**（Week 5-6的AI查询引擎）：
- LLM API Key申请和配额
- 模型响应解析的准确性
- 并发查询的稳定性

**应对方案**：
- 先集成最容易的模型（ChatGPT API），再扩展其他模型
- 结果解析先用LLM辅助（让GPT分析自己的输出），再写规则提取
- 异步并发+超时控制+错误重试

---

## 五、代码架构（MVP版）

```
backend/
├── app/
│   ├── main.py              # FastAPI入口
│   ├── models/              # SQLAlchemy模型
│   │   ├── user.py
│   │   ├── company.py
│   │   └── query_result.py
│   ├── api/v1/
│   │   ├── auth.py          # 注册/登录
│   │   ├── companies.py     # 企业CRUD
│   │   ├── geo_score.py     # GEO评分
│   │   └── reports.py       # 报告
│   ├── services/
│   │   ├── llm_client.py    # AI模型查询（Week 5-6）
│   │   ├── query_scheduler.py # 并发调度
│   │   ├── result_parser.py # 结果解析
│   │   └── geo_score.py     # 评分计算（Week 7-8）
│   └── core/
│       ├── config.py
│       ├── security.py
│       └── database.py
├── alembic/                 # 数据库迁移
├── requirements.txt
└── Dockerfile

frontend/
├── src/
│   ├── app/
│   │   ├── dashboard/       # 主页面
│   │   ├── login/           # 登录
│   │   └── register/        # 注册
│   └── components/
│       ├── GeoScoreCard     # 评分卡片
│       ├── TrendChart       # 趋势图
│       └── CompetitorTable  # 竞品对比
├── package.json
└── next.config.js
```

**和现有backend/app/的差异**：无需改动现有骨架。现有代码已经是FastAPI+SQLAlchemy+Alembic。MVP只需要：
1. 加 services/ 目录（查询引擎+评分引擎）
2. 加 query_result.py 模型
3. 加 geo_score.py 和 reports.py 路由

---

## 六、技术栈快速启动

### 第1天就能看到效果

```bash
# 克隆 + 启动
git clone ...
cd GEO-Industry-Engine

# 后端启动
docker compose up -d postgres  # 启动数据库
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head           # 建表
uvicorn app.main:app --reload  # 启动API

# 验证
curl http://localhost:8000/health
# {"status": "ok", "version": "0.1.0"}

curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"pass123","name":"Test"}'
# {"access_token": "...", "user": {...}}
```

### 已有代码可复用部分

| 模块 | 现有状态 | MVP复用方式 |
|------|---------|-----------|
| 数据库连接 | app/database.py ✅ | 直接使用 |
| 用户模型 | app/models/user.py ✅ | 直接使用 |
| 认证API | app/api/v1/auth.py ✅ | 直接使用 |
| 企业模型 | app/models/company.py ✅ | 直接使用 |
| 企业API | app/api/v1/users.py ✅ | 扩展CRUD |
| JWT安全 | app/core/security.py ✅ | 直接使用 |
| 配置 | app/core/config.py ✅ | 直接使用 |
| 前端骨架 | frontend/ ✅ | 直接使用 |
| Docker | docker-compose.yml ✅ | 直接使用 |
| 迁移框架 | alembic/ ✅ | 直接使用 |

**已有代码覆盖率**：后端骨架完成度约40%。需要新增：services/层(查询引擎+评分引擎)、query_result模型、geo_score和reports路由。

---

## 七、执行风险与应对

| 风险 | 概率 | 影响 | 应对 |
|------|------|------|------|
| LLM API不可用/限流 | 中 | 高 | 混用多模型，降级策略 |
| 结果解析不准确 | 中 | 中 | LLM辅助解析+人工校对 |
| 评分与用户感知偏差 | 高 | 中 | 反馈按钮+持续校准(16号文档§五)|
| 开发人力不足 | 中 | 高 | 先做核心路径，砍非核心功能 |
| 支付集成复杂 | 低 | 中 | 用Stripe/Paddle现成SDK |

---

## 八、验收标准

| 里程碑 | 验收标准 |
|--------|---------|
| Week 2 | docker compose up后API可访问 |
| Week 4 | 用户注册->登录->添加企业 |
| Week 6 | 向3个模型发送10个查询，结果入库 |
| Week 8 | 企业GEO评分可计算(4因子) |
| Week 10 | Dashboard展示评分+竞品对比 |
| Week 12 | 产品上线，首批用户可使用 |

---

## 九、关联文档

| 文档 | 关系 |
|------|------|
| 11_MVP范围.md | 规划依据 |
| 16_GEO评分算法与模拟验证.md | 评分算法(本计划使用简版)|
| 20_数据生产机制与初始化策略.md | 数据来源 |
| 22_GEO测量方法论.md | 测量协议(本计划使用简化版)|
| 05_技术架构.md | 技术选型依据 |
| 18_工程实践与运维设计.md | CI/CD + 测试 |
"""

filepath = os.path.join("D:\\GEO-IE", "docs", "24_执行方案与90天计划.md")
with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("24 created: " + str(os.path.getsize(filepath)) + " bytes")