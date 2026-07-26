import os

p01 = os.path.join("D:\\GEO-IE\\docs\\01_产品架构PRD.md")
c = open(p01, "r", encoding="utf-8").read()

old = """### AI模型智能库影响说明

AI模型智能库不是独立系统，而是GEO数据资产中心的核心智能子模块。它影响：

- **GEO评分引擎**：模型成为评分变量——不同模型的引用行为、来源偏好、行业倾向直接影响企业的GEO评分
- **Scanner Agent**：根据行业+目标企业+模型权重选择扫描策略（如医疗企业重点扫描Claude/ChatGPT/Perplexity）
- **Content Agent**：针对不同模型偏好生成差异化内容策略
- **产业导航地图**：模型-行业热度矩阵为地图提供\"哪个行业在哪个模型最火\"的数据层

内部架构：

```
GEO数据资产中心
├── 数据层：行业/企业/Prompt/回答/研究资料
└── 智能层：AI Model Intelligence
    ├── Model Profile（模型画像）
    ├── Model Behavior（行为模式）
    ├── Industry Preference（行业偏好）
    ├── Source Preference（来源偏好）
    ├── Query Result（查询结果）
    └── Ranking Signal（排名信号）
```"""

new = """### AI模型智能库 — 5层研究系统

AI模型智能库不是简单的大模型列表，而是由5层研究结构组成的系统。

---

#### 第1层：全球AI模型生态地图

持续维护的模型注册表，定位每个模型的GEO价值。

**全球通用模型**

| 模型 | 公司 | GEO价值 |
|------|------|---------|
| ChatGPT | OpenAI | 全球最大综合AI入口，品牌认知影响最大 |
| Gemini | Google | 搜索生态+网页+Maps+YouTube天然优势 |
| Claude | Anthropic | 长文本、企业知识、专业分析最佳 |
| Perplexity | Perplexity AI | AI搜索引用机制，最接近GEO目标 |
| Grok | xAI | 社交内容、实时信息优势 |
| Copilot | Microsoft | 企业办公生态入口 |
| Llama生态 | Meta | 开源生态，企业私有化部署 |

**中国市场模型**

| 模型 | 公司 | GEO价值 |
|------|------|---------|
| DeepSeek | 深度求索 | 中文推理、国内用户高速增长 |
| 通义千问 | 阿里 | 企业、电商生态 |
| 文心 | 百度 | 搜索生态 |
| Kimi | 月之暗面 | 长文本、知识工作 |
| 豆包 | 字节 | C端流量最大 |
| 智谱清言 | 智谱 | 企业市场 |

---

#### 第2层：模型用户画像

GEO关心的是：**谁在使用这些模型？他们影响什么决策？**

**ChatGPT**
- 用户群体：企业管理者、开发者、咨询顾问、学生、全球知识工作者
- 优势行业：★★★★★ 软件、咨询、教育、营销、B2B
- 决策影响力：高（直接影响购买决策）

**Gemini**
- 用户群体：Google生态用户
- 优势行业：★★★★★ 旅游、本地服务、电商、消费品牌
- 天然连接：Search、Maps、YouTube、Workspace

**Claude**
- 用户群体：企业专业人士、法律/咨询/研发从业者
- 优势行业：★★★★★ 法律、咨询、企业研究、软件开发
- 特征：知识工作和企业自动化最深入

**Perplexity**
- 定位：GEO测试实验室
- 特征：天然展示「引用来源、网站、品牌」，最适合评估GEO效果

---

#### 第3层：行业X模型矩阵

商业护城河。核心数据产品。

| 行业 | 第一推荐模型 | 第二推荐 | 第三 | 第四 |
|------|-----------|---------|------|------|
| 医疗 | Claude ★★★★★ | ChatGPT ★★★★★ | Gemini ★★★★ | Perplexity ★★★★ |
| 工业制造 | ChatGPT ★★★★★ | Claude ★★★★★ | Gemini ★★★★ | DeepSeek ★★★★ |
| 电商 | Gemini ★★★★★ | ChatGPT ★★★★★ | 通义千问 ★★★★★ | 豆包 ★★★★ |
| 软件开发 | Claude ★★★★★ | ChatGPT ★★★★★ | Gemini ★★★★ | Perplexity ★★★ |
| 教育 | ChatGPT ★★★★★ | Gemini ★★★★ | Perplexity ★★★★ | Claude ★★★ |
| 金融 | Claude ★★★★★ | ChatGPT ★★★★★ | DeepSeek ★★★★ | Perplexity ★★★ |

数据来源：ai_query_results 查询样本的统计分析 + 定期校准

---

#### 第4层：Prompt知识库

最重要的数据资产。不是查询日志，而是**GEO Prompt Database**。

每条记录：

```
问题：中国工业机器人十大企业有哪些？
模型：ChatGPT
回答：[ABB, 新松, 埃斯顿, ...]
引用来源：[xxx官网, xxx维基百科, ...]
出现频率：82%
行业：工业制造
```

用途：
- 每天监控：谁在上升、谁在下降、为什么
- 发现新竞争者：AI回答中出现了哪些新企业
- 分析引用来源变化：模型在改变它的参考来源

---

#### 第5层：AI品牌排名系统

最终输出产品。类似AI时代的Alexa / SimilarWeb / Ahrefs。

| 企业 | ChatGPT评分 | Gemini评分 | Claude评分 | Perplexity评分 | 综合GEO评分 |
|------|-----------|-----------|-----------|-------------|-----------|
| 华为 | 92 | 88 | 85 | 90 | 89 |
| 某企业 | XX | XX | XX | XX | XX |

输出到：
- AI可见度增长系统的Dashboard首页
- 产业导航的企业画像页面
- 交易市场的服务商信用评价"""

c = c.replace(old, new)

open(p01, "w", encoding="utf-8").write(c)
print("01 done")