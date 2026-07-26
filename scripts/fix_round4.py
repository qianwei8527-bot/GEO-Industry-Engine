import os
base = "D:\\GEO-IE\\docs"

# Fix 23: data source levels - properly escaped
p23 = os.path.join(base, "23_合规与风险规范.md")
c = open(p23, "r", encoding="utf-8").read()
levels = "\n\n---\n\n## \u6570\u636e\u6765\u6e90\u7b49\u7ea7\n\n| \u7b49\u7ea7 | \u8bf4\u660e | \u7528\u9014 |\n|------|------|------|\n"
levels += "| L0 \u81ea\u586b | \u7528\u6237\u81ea\u884c\u586b\u5199\u7684\u4fe1\u606f | \u53c2\u8003\u4fe1\u606f |\n"
levels += "| L1 \u5ba1\u6838\u8fc7\u7684\u6570\u636e | \u5e73\u53f0\u5ba1\u6838\u540e\u7684\u6570\u636e | \u57fa\u7840\u4fe1\u4efb |\n"
levels += "| L2 \u7b2c\u4e09\u65b9\u8bc1\u660e | \u7b2c\u4e09\u65b9\u6743\u5a01\u673a\u6784\u7684\u8bc1\u660e | \u8ba4\u8bc1\u6570\u636e |\n"
levels += "| L3 \u5e02\u573a\u9a8c\u8bc1 | \u5e02\u573a\u9a8c\u8bc1\u7684\u6570\u636e | \u9ad8\u4fe1\u4efb\u6570\u636e |\n"
levels += "| L4 AI\u4ea4\u53c9\u9a8c\u8bc1 | \u591a\u4e2aAI\u6a21\u578b\u4ea4\u53c9\u786e\u8ba4\u7684\u6570\u636e | \u6700\u9ad8\u4fe1\u4efb\u6570\u636e |\n"
c += levels
open(p23, "w", encoding="utf-8").write(c)
print("23 fixed")

# Re-run 26, 27, 25, 12 updates
# 26: Add 4 protocols
p26 = os.path.join(base, "26_GEO产业内核与开放协议.md")
c = open(p26, "r", encoding="utf-8").read()
new_protocols = "\n| Capability Protocol | \u63cf\u8ff0\u80fd\u529b\u7684\u8868\u8fbe\u65b9\u5f0f | REST API |\n| Evidence Protocol | \u8bc1\u660e\u771f\u5b9e\u6027\u7684\u65b9\u5f0f | \u94fe\u8bc1+API |\n| Contribution Protocol | \u8bb0\u5f55\u751f\u6001\u8d21\u732e\u7684\u65b9\u5f0f | \u4e8b\u4ef6\u91c7\u96c6 |\n| Evolution Protocol | \u4ea7\u4e1a\u53d8\u5316\u5982\u4f55\u540c\u6b65 | WebSocket |"
c += new_protocols
open(p26, "w", encoding="utf-8").write(c)
print("26 fixed")

# 27: Add radar
p27 = os.path.join(base, "27_GEO产业数字孪生与演化模拟.md")
c = open(p27, "r", encoding="utf-8").read()
radar = "\n\n---\n\n## \u4ea7\u4e1a\u96f7\u8fbe\n\n| \u76d1\u6d4b\u7ef4\u5ea6 | \u5185\u5bb9 | \u9891\u7387 |\n|------------|------|------|\n| \u65b0\u5174\u8d5b\u9053 | \u65b0\u51fa\u73b0\u7684\u4ea7\u4e1a\u5206\u652f | \u6bcf\u5468 |\n| \u589e\u957f\u4f01\u4e1a | GEO\u8bc4\u5206\u589e\u957f\u6700\u5feb\u7684\u4f01\u4e1a | \u6bcf\u5929 |\n| \u6280\u672f\u53d8\u5316 | \u65b0\u6280\u672f\u51fa\u73b0\u7684\u9891\u7387\u548c\u5f71\u54cd | \u6bcf\u5929 |\n| \u4eba\u624d\u6d41\u52a8 | \u4eba\u624d\u6d41\u5411\u53d8\u5316 | \u6bcf\u5468 |\n| \u8d44\u672c\u65b9\u5411 | \u878d\u8d44\u3001\u6295\u8d44\u8d8b\u52bf | \u6bcf\u5468 |\n| \u5730\u533a\u673a\u4f1a | \u533a\u57dfGEO\u6307\u6570\u53d8\u5316 | \u6bcf\u6708 |\n"
c += radar
open(p27, "w", encoding="utf-8").write(c)
print("27 fixed")

# 25: Add relationship weight
p25 = os.path.join(base, "25_GEO产业本体模型.md")
c = open(p25, "r", encoding="utf-8").read()
rel_weight = "\n\n### \u5173\u7cfb\u5f3a\u5ea6\u8ba1\u7b97\n\n\u5173\u7cfb\u5f3a\u5ea6 = \u9891\u7387 x \u65f6\u95f4 x \u5f71\u54cd\u8303\u56f4 x \u53ef\u4fe1\u5ea6 x \u7ed3\u679c\u53cd\u9988\n"
c += rel_weight
open(p25, "w", encoding="utf-8").write(c)
print("25 fixed")

# 12: Add decision engine
p12 = os.path.join(base, "12_GEO用户行为与AI决策路径模型.md")
c = open(p12, "r", encoding="utf-8").read()
decision = "\n\n---\n\n## GEO\u51b3\u7b56\u5f15\u64ce\n\n\u7528\u6237\u4e0d\u662f\u6765\u67e5\u8d44\u6599\uff0c\u800c\u662f\u8ba9\u7cfb\u7edf\u8f85\u52a9\u51b3\u7b56\u3002\u4f8b\u5982\uff1a\u201c\u6211\u5e94\u8be5\u8fdb\u5165\u533b\u7597AI\u8fd8\u662f\u6559\u80b2AI\uff1f\u201d\u7cfb\u7edf\u5206\u6790\u5e02\u573a\u589e\u957f\u3001\u7ade\u4e89\u7a0b\u5ea6\u3001\u4eba\u624d\u4f9b\u5e94\u3001\u8d44\u672c\u6d41\u5411\u3001\u653f\u7b56\u3001\u81ea\u8eab\u80fd\u529b\uff0c\u8f93\u51fa\u63a8\u8350\u548c\u539f\u56e0\u3002"
c += decision
open(p12, "w", encoding="utf-8").write(c)
print("12 fixed")
print("All fixed")