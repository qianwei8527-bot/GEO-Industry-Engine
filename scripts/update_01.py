# -*- coding: utf-8 -*-
c = open("D:\\GEO-IE\\docs\\01_产品架构PRD.md", "r", encoding="utf-8").read()

old_mod = "| **趋势预测** | 基于历史数据自动生成GEO评分/曝光量的预测趋势线"
new_mod = '| **趋势预测** | 基于历史数据自动生成GEO评分/曝光量的预测趋势线 |\n| **竞争对标** | 与竞争对手的AI可见度对比分析，支持多企业对比，展示差距与提升机会，自动生成竞争策略建议 |\n| **ROI计算器** | 量化GEO评分提升带来的AI曝光增量、流量预估、商业价值换算，支持情景模拟 |\n| **一键优化** | 基于分析结果自动生成优化方案，确认后一键部署内容调整，支持定时执行'
c = c.replace(old_mod, new_mod)

old_end = "每一层都支持：**展示**（可视化呈现）、**连接**（点击跳转关联信息）、**评论**（用户参与讨论）、**自动更新**（数据层实时同步变化）。"
new_cross = old_end + '\n\n**跨层能力**\n\n**GEO成熟度模型** -- 每层中的企业/主体按成熟度分为 L1-L5：\n- L1 未入局：在AI搜索中仅有被动存在\n- L2 被动存在：有基础信息但无系统性优化\n- L3 主动优化：有策略地提升AI可见度\n- L4 系统管理：建立完整的GEO管理体系\n- L5 行业引领：成为AI搜索中的行业标准\n\n**最佳实践案例库** -- 每层展示该层的成功案例和方法论：\n- 案例：该层中做得好的企业实践\n- 方法论：该层的优化方法论和流程参考\n- 贡献：用户可提交自己的实践案例\n\n**工具链标注** -- 每层标注可用的工具/平台/服务商生态：\n- 查看该层推荐的工具链\n- 工具链接直接跳转交易市场\n- 用户可提交工具推荐'
c = c.replace(old_end, new_cross)

old_dev = "跨平台AI身份统一管理"
new_dev = old_dev + '\n\n**工具链生态（Toolchain Ecosystem）** -- 每个趋势方向标注相关的工具和技术栈\n\n**跨行业对比（Cross-Industry Comparison）** -- 所有地图支持跨行业横向对比：行业间GEO指数排名、AI可见度差异、增长速度对比'
c = c.replace(old_dev, new_dev)

old_data = "| 研究资料库 | AI自动生成的行业研究报告、趋势预测分析 | AI研究引擎 |"
new_data = old_data + '\n| API数据服务 | 企业/行业GEO数据API访问，支持按调用量计费 | 数据服务层 |'
c = c.replace(old_data, new_data)

open("D:\\GEO-IE\\docs\\01_产品架构PRD.md", "w", encoding="utf-8").write(c)
print("01_产品架构PRD.md updated")