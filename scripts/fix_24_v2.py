import os
p24 = os.path.join("D:\\GEO-IE", "docs", "24_执行方案与90天计划.md")
c = open(p24, "r", encoding="utf-8").read()

# Find sections using Unicode escapes for Chinese text
s4_marker = '\u0023\u0023\u0023\u0020\u0020\u0020\u56db\u3001\u5173\u952e\u8def\u5f84'
# "### 四、关键路径"
s4_start = c.find('\u0023\u0023\u0023\u0020\u0020\u56db\u3001\u5173\u952e\u8def\u5f84')

# Actually, let me just use position-based approach
# Find section 3 header
s3_header = c.find('\u0023\u0023\u0023\u0020\u0020\u4e09\u300190\u5929\u5468\u8ba1\u5212')
# "### 三、90天周计划"

# Find section 4 header  
s4_header = c.find('\u0023\u0023\u0023\u0020\u0020\u56db\u3001\u5173\u952e\u8def\u5f84')
# "### 四、关键路径"

if s3_header < 0 or s4_header < 0:
    # Fall back to simpler search
    s3_header = c.find('90\u5929\u5468\u8ba1\u5212')  # 90天周计划
    s4_header = c.find('\u5173\u952e\u8def\u5f84')  # 关键路径
    s3_header = c.rfind('\u0023', 0, s3_header)  # Find the ### before it

if s3_header >= 0 and s4_header > s3_header:
    # Find where the week-by-week content starts (after section 3 intro)
    rest = c[s3_header:s4_header]
    wk_start = rest.find('\u7b2c1-2\u5468')  # 第1-2周
    if wk_start >= 0:
        content_start = s3_header + wk_start
        
        new_plan = """### 第1-2周：基础搭建 + API契约 + 前端原型

| 角色 | 任务 | 产出 |
|------|------|------|
| 后端 | 数据库Schema + FastAPI骨架 + CI/CD + Docker | docker compose up可用 |
| 前端 | 项目脚手架 + Figma原型 + Mock数据设计 | 所有页面的静态原型 |
| 同步 | **前后端共同定义OpenAPI契约** | api-contract.yaml |
| 里程碑 | docker compose up后API可访问，前端原型可浏览 |

### 第3-4周：用户系统 + 前端页面

| 角色 | 任务 | 产出 |
|------|------|------|
| 后端 | 用户注册/登录API + 企业CRUD + JWT鉴权 | POST /auth/register/login |
| 前端 | 注册页 + 登录页 + 企业添加页 + Mock Dashboard | 3个页面 + 1个Mock看板 |
| 同步 | **联调注册/登录流程（首次前后端握手）** | 注册登录添加企业链路跑通 |
| 里程碑 | 用户可注册登录添加企业（前后端已连通） |

### 第5-6周：AI查询引擎 + 前端完整UI

| 角色 | 任务 | 产出 |
|------|------|------|
| 后端 | LLM API集成(ChatGPT+Gemini+DeepSeek) + 并发查询调度 + 结果解析 | 向3个模型发送10个Prompt，结果入库 |
| 后端(备用) | Mock AI查询服务（降级方案，返回预设数据） | LLM API不通时系统仍可用 |
| 前端 | Dashboard完整页面(GEO评分卡片+趋势图+企业列表) + 竞品对比页 | 所有UI已用Mock数据展示 |
| 同步 | 前端用Mock AI数据验证Dashboard展示 | Mock数据到评分卡片到趋势图完整展示 |
| 里程碑 | AI查询结果入库 | Dashboard用Mock数据可完整展示 |

### 第7-8周：GEO评分引擎 + 前后端全链路

| 角色 | 任务 | 产出 |
|------|------|------|
| 后端 | 4因子GEO评分计算 + GET /geo-score + 趋势数据API | 评分可计算，API可用 |
| 前端 | 接入真实GEO评分API + 评分变化趋势图 + 竞品对比数据 | Mock换真实数据 |
| 同步 | **首次全链路联调**（注册到查询到评分到展示） | 全流程可用 |
| 里程碑 | 输入企业ID到AI查询到评分到Dashboard展示完整跑通 |

### 第9-10周：报告 + 支付 + 优化

| 角色 | 任务 | 产出 |
|------|------|------|
| 后端 | 报告API + 邮件周报 + Stripe/Paddle支付集成 | GET /reports, POST /subscribe |
| 前端 | 报告展示页 + 支付页 + 账户管理 + 界面优化 | 完整用户界面 |
| 同步 | 集成测试 + 支付流程联调 | 注册到付费到使用完整闭环 |
| 里程碑 | Free/Pro两层可用，付费后可看竞品对比 |

### 第11-12周：上线

| 角色 | 任务 | 产出 |
|------|------|------|
| 后端 | 日志+监控+错误追踪+性能优化 | 生产环境就绪 |
| 前端 | 上线前测试 + SEO基础 + 错误边界 | 前端就绪 |
| 同步 | 上线检查 + 首批种子用户接入 | 产品上线 |"""
        
        c = c[:content_start] + new_plan + c[s4_header:]
        print("Section 3 replaced")
    else:
        print("Week marker not found")
else:
    print("Section headers not found")

open(p24, "w", encoding="utf-8").write(c)
print("24 fixed: " + str(os.path.getsize(p24)) + " bytes")