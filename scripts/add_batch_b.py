import os
# Batch B: update 5 existing docs

# 20: Add incentive mechanism + cost control
p20 = os.path.join("D:\\GEO-IE", "docs", "20_数据生产机制与初始化策略.md")
c = open(p20, "r", encoding="utf-8").read()
new_20 = """## 八、激励机制

### 8.1 企业贡献激励

| 贡献行为 | 激励 | 说明 |
|---------|------|------|
| 提交企业信息 | GEO评分+5 | 补充越完整加分越多 |
| 提交案例 | 案例曝光+认证积分 | 案例出现在产业地图 |
| 数据纠错 | 纠错积分+社区等级 | 积分可兑换认证折扣 |
| 内容贡献 | 内容曝光+专家认证 | 高质量内容获专家标识 |

### 8.2 服务商贡献激励

| 贡献行为 | 激励 |
|---------|------|
| 提交服务案例 | 案例展示+搜索排名加权 |
| 完善服务信息 | 服务商认证等级提升 |
| 参与社区问答 | 曝光+专家标识 |

## 九、成本控制策略

### 9.1 LLM API成本控制

| 策略 | 说明 | 预估节省 |
|------|------|---------|
| 分层采样 | 重点企业每天扫，普通企业每周扫 | 60% |
| 缓存复用 | 相同行业+相同Prompt 24h内复用 | 30% |
| 混合调度 | 先用免费额度，超出后降频 | 20% |
| 模拟基线 | API预算不足时用历史数据推演 | 100%替代 |

### 9.2 缓存规则

| 缓存类型 | 有效期 | 失效条件 |
|---------|--------|---------|
| 模型查询结果 | 4小时 | 有新数据到达 |
| GEO评分 | 1小时 | 新查询结果更新 |
| 企业信息 | 24小时 | 企业主动更新 |"""

old_20 = "## 七、数据质量框架"
c = c.replace(old_20, old_20 + new_20)
open(p20, "w", encoding="utf-8").write(c)
print("20 done")

# 16: Add feedback calibration
p16 = os.path.join("D:\\GEO-IE", "docs", "16_GEO评分算法与模拟验证.md")
c = open(p16, "r", encoding="utf-8").read()
new_16 = "\n\n## 五、用户反馈校准\n\n### 5.1 反馈机制\n\n| 反馈类型 | 触发方式 | 处理方式 |\n|---------|---------|---------|\n| 评分感知偏差 | 用户点击\"评分不准？\"按钮 | 记录偏差，标记该企业评分待校准 |\n| 排名感知偏差 | 用户提交自己的排名观察 | 交叉验证后更新排名 |\n| 优化效果反馈 | 用户确认优化动作完成 | 启动重扫+对比分析 |\n\n### 5.2 反馈数据应用\n\n积累100条反馈后，启动权重校准：\n1. 分析反馈中评分偏差的分布\n2. 修正偏差较大的因子权重\n3. 发布新版评分算法\n"
old_16 = "## 四、关联文档"
c = c.replace(old_16, new_16 + old_16)
open(p16, "w", encoding="utf-8").write(c)
print("16 done")

# 17: Add cold start strategy
p17 = os.path.join("D:\\GEO-IE", "docs", "17_产品定义与商业模式.md")
c = open(p17, "r", encoding="utf-8").read()
new_17 = "\n\n### 交易市场冷启动策略\n\n| 阶段 | 策略 | 目标 |\n|------|------|------|\n| 冷启动(0-3月) | 主动签约10-20家GEO服务商，免费入驻，0佣金 | 形成基础供给 |\n| 增长(3-6月) | 依托监测客户的优化需求自动生成订单推送给服务商 | 供需匹配 |\n| 成熟(6月+) | 供给达标后启动抽佣(5-10%) | 收入变现 |\n"
old_17 = "### 2.4 认证收入"
c = c.replace(old_17, new_17 + old_17)
open(p17, "w", encoding="utf-8").write(c)
print("17 done")

# 14: Add MVP semi-automation path
p14 = os.path.join("D:\\GEO-IE", "docs", "14_GEO实体智能与信息供应链模型.md")
c = open(p14, "r", encoding="utf-8").read()
new_14 = "\n\n### MVP实现路径\n\n| 阶段 | 实体画像方式 | 自动程度 |\n|------|------------|---------|\n| MVP | 用户手动填写+系统自动搜索补充+用户一键确认 | 半自动 |\n| v2 | 多源信息自动抽取+实体消歧 | 全自动+人工审核 |\n| v3 | 实时更新+自动消歧+NLP推理 | 全自动 |\n"
old_14 = "### 5.1 EntityProfile"
c = c.replace(old_14, new_14 + old_14)
open(p14, "w", encoding="utf-8").write(c)
print("14 done")

# 06: Add feedback button
p06 = os.path.join("D:\\GEO-IE", "docs", "06_前端设计.md")
c = open(p06, "r", encoding="utf-8").read()
old_06 = "- Dashboard：GEO评分趋势图 + AI提及热力图 + 三线预测图 + 竞争对标仪表盘(多企业对比) + ROI计算器(效果模拟)"
new_06 = old_06 + "\n- 评分反馈按钮：\"评分不准？告诉我们\" → 触发反馈表，记录用户感知偏差，校准评分"
if old_06 in c:
    c = c.replace(old_06, new_06)
    open(p06, "w", encoding="utf-8").write(c)
    print("06 done")
else:
    print("06 marker not found")

print("Batch B complete")