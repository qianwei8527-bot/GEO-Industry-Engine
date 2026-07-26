import os

p24 = os.path.join("D:\\GEO-IE", "docs", "24_执行方案与90天计划.md")
c = open(p24, "r", encoding="utf-8").read()

# ===== 1. Replace the old section 3 (90-day plan) with parallel version =====
old_start = "### 第1-2周：基础搭建"
old_end = "### 四、关键路径"

start_idx = c.find(old_start)
end_idx = c.find(old_end)

if start_idx >= 0 and end_idx > start_idx:
    new_plan = """### 第1-2周：基础搭建 + API契约 + 前端原型

| 角色 | 任务 | 产出 |
|------|------|------|
| 后端 | 数据库Schema + FastAPI骨架 + CI/CD + Docker | docker compose up可用 |
| 前端 | 项目脚手架 + Figma原型 + Mock数据设计 | 所有页面的静态原型 |
| 🔗 同步 | **前后端共同定义OpenAPI契约** | api-contract.yaml |
| 里程碑 | docker compose up后API可访问，前端原型可浏览 |

### 第3-4周：用户系统 + 前端页面

| 角色 | 任务 | 产出 |
|------|------|------|
| 后端 | 用户注册/登录API + 企业CRUD + JWT鉴权 | POST /auth/register/login |
| 前端 | 注册页 + 登录页 + 企业添加页 + Mock Dashboard | 3个页面 + 1个Mock看板 |
| 🔗 同步 | **联调注册/登录流程（首次前后端握手）** | 注册→登录→添加企业 链路跑通 |
| 里程碑 | 用户可注册登录添加企业（前后端已连通） |

### 第5-6周：AI查询引擎 + 前端完整UI

| 角色 | 任务 | 产出 |
|------|------|------|
| 后端 | LLM API集成(ChatGPT+Gemini+DeepSeek) + 并发查询调度 + 结果解析 | 向3个模型发送10个Prompt，结果入库 |
| 后端(备用) | **Mock AI查询服务**（降级方案，返回预设数据） | LLM API不通时系统仍可用 |
| 前端 | Dashboard完整页面(GEO评分卡片+趋势图+企业列表) + 竞品对比页 | 所有UI已用Mock数据展示 |
| 🔗 同步 | **前端用Mock AI数据验证Dashboard展示** | Mock数据→评分卡片→趋势图完整展示 |
| 里程碑 | AI查询结果入库 || Dashboard用Mock数据可完整展示 |

### 第7-8周：GEO评分引擎 + 前后端全链路

| 角色 | 任务 | 产出 |
|------|------|------|
| 后端 | 4因子GEO评分计算 + GET /geo-score/{id} + 趋势数据API | 评分可计算，API可用 |
| 前端 | **接入真实GEO评分API** + 评分变化趋势图 + 竞品对比数据 | Mock换真实数据 |
| 🔗 同步 | **首次全链路联调**（注册→查询→评分→展示） | 全流程可用 |
| 里程碑 | 输入企业ID→AI查询→评分→Dashboard展示 完整跑通 |

### 第9-10周：报告 + 支付 + 优化

| 角色 | 任务 | 产出 |
|------|------|------|
| 后端 | 报告API + 邮件周报 + Stripe/Paddle支付集成 | GET /reports, POST /subscribe |
| 前端 | 报告展示页 + 支付页 + 账户管理 + 界面优化 | 完整用户界面 |
| 🔗 同步 | **集成测试 + 支付流程联调** | 注册→付费→使用 完整闭环 |
| 里程碑 | Free/Pro两层可用，付费后可看竞品对比 |

### 第11-12周：上线

| 角色 | 任务 | 产出 |
|------|------|------|
| 后端 | 日志+监控+错误追踪+性能优化 | 生产环境就绪 |
| 前端 | 上线前测试 + SEO基础 + 错误边界 | 前端就绪 |
| 🔗 同步 | 上线检查 + 首批种子用户接入 | 产品上线 |
| 里程碑 | 首批用户可注册使用 |"""

    c = c[:start_idx] + new_plan + c[end_idx:]
    print("[PASS] Section 3 replaced")
else:
    print("[FAIL] Markers not found")

# ===== 2. Update 关键路径 to show parallel paths =====
old_path = """### 四、关键路径

```
Week 2: Docker + 数据库            │
                                   │ 关键路径
Week 4: 用户 + 企业注册             │（不可并行）
                                   │
Week 6: AI查询引擎 ★★★★★ 最难      ┘
                                   ┐
Week 8: GEO评分引擎                │ 可并行
                                   │
Week 10: Dashboard + 竞品对比       │
                                   │
Week 12: 报告 + 发布               ┘"""

new_path = """### 四、关键路径

```
Week 1: API契约定义 🔗  ← 前后端对齐
Week 2: 后端骨架 + 前端原型  ← 并行
Week 4: 注册登录联调 🔗    ← 首次握手
Week 6: AI查询引擎(Mock就绪)  ← 最难点(有降级)
Week 8: 全链路联调 🔗      ← 所有系统第一次跑通
Week 10: 支付联调 🔗      ← 商业闭环
Week 12: 上线
```

**并行策略**：前端从第1周就用Mock数据推进，不等后端。后端专注核心引擎。第4周首次联调，第8周全链路联调。避免第9周才第一次握手。

**AI查询引擎风险**：Week 5-6 同步准备Mock AI服务。如果LLM API集成受阻，Mock服务可保证前端开发和评分引擎不受阻塞。"""

c = c.replace(old_path, new_path)
print("[PASS] 关键路径 updated")

# ===== 3. Add 前后端同步策略 section after 关键路径 =====
old_after_path = "**AI查询引擎风险**：Week 5-6 同步准备Mock AI服务。如果LLM API集成受阻，Mock服务可保证前端开发和评分引擎不受阻塞。"

new_sync = """

---

## 前后端同步策略

### 1. API契约先行

每轮Sprint开始前，前后端共同定义本次Sprint的OpenAPI契约。

```
Week 1: 定义 auth + companies 的API契约
Week 3: 定义 geo-score 的API契约
Week 5: 定义 reports 的API契约
Week 7: 定义 payments 的API契约
```

契约文件统一放在 `docs/api-contracts/` 目录下，前后端共同遵守。

### 2. Mock数据策略

| 阶段 | 前端数据源 | 后端状态 |
|------|-----------|---------|
| Week 1-4 | 静态Mock JSON（本地文件） | 数据库+API开发中 |
| Week 5-6 | Mock AI Server（预设返回） | LLM集成+评分开发中 |
| Week 7-8 | 部分真实API + 部分Mock | 核心API完成 |
| Week 9+ | 全部真实API | 所有API完成 |

### 3. 联调节奏

| 频次 | 方式 | 内容 |
|------|------|------|
| 每天 | 自动 (CI) | Contract Test（API格式一致）|
| 每周 | 手动 | 端到端走查一个完整流程 |
| 里程碑 | 全员 | 全链路验收 |

### 4. 接口变更流程

```
需要改API → 先更新契约文件 → 通知对方 → 同步修改代码 → 测试验证
```

禁止在未通知对方的情况下修改API返回值格式。
"""

c = c.replace(old_after_path, old_after_path + new_sync)
print("[PASS] 同步策略 added")

# ===== 4. Update 执行风险 to add coordination risks =====
old_risk = "| 开发人力不足 | 中 | 高 | 先做核心路径，砍非核心功能 |"
new_risk = """| 开发人力不足 | 中 | 高 | 先做核心路径，砍非核心功能 |
| 前后端接口不一致（联调发现晚）| 中 | 中 | API契约先行+Mock数据+第4周首次联调 |
| 前端依赖后端API阻塞进度 | 高 | 中 | Mock数据策略保障前端独立推进 |
| AI查询引擎延期影响全链路 | 中 | 高 | Mock AI Serve作为降级方案 |"""

c = c.replace(old_risk, new_risk)
print("[PASS] 风险 updated")

open(p24, "w", encoding="utf-8").write(c)
print("24 updated: " + str(os.path.getsize(p24)) + " bytes")