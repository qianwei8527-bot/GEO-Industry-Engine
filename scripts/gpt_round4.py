import os
base = "D:\\GEO-IE\\docs"

# === 28: GEO产业搜索引擎 ===
c28 = "# GEO\u4ea7\u4e1a\u641c\u7d22\u5f15\u64ce\n\n> \u4e0d\u662f\u5173\u952e\u8bcd\u5339\u914d\uff0c\u800c\u662f\u7406\u89e3\u201c\u6211\u8981\u627e\u4ec0\u4e48\u201d\u80cc\u540e\u7684\u771f\u5b9e\u9700\u6c42\u3002\n\n---\n\n## \u4e00\u3001\u4ece\u5173\u952e\u8bcd\u641c\u7d22\u5230\u610f\u56fe\u641c\u7d22\n\n| \u7ef4\u5ea6 | \u4f20\u7edf\u641c\u7d22 | GEO\u641c\u7d22 |\n|---------|-------------|----------|\n| \u8f93\u5165 | \u5173\u952e\u8bcd | \u81ea\u7136\u8bed\u8a00 |\n| \u7406\u89e3 | \u5b57\u9762\u5339\u914d | \u610f\u56fe\u89e3\u6790 |\n| \u5339\u914d | \u9875\u9762\u7d22\u5f15 | \u5b9e\u4f53\u77e5\u8bc6\u56fe\u8c31 |\n| \u6392\u5e8f | PageRank | GEO\u8bc4\u5206+\u76f8\u5173\u6027+\u4fe1\u4efb\u5ea6 |\n\n## \u4e8c\u3001\u67e5\u8be2\u7406\u89e3\u7ba1\u9053\n\n\u8f93\u5165\u81ea\u7136\u8bed\u8a00 \u2192 \u610f\u56fe\u5206\u7c7b(5\u7c7b) \u2192 \u5b9e\u4f53\u63d0\u53d6(\u884c\u4e1a/\u80fd\u529b/\u5730\u57df/\u9884\u7b97) \u2192 \u6761\u4ef6\u6620\u5c04 \u2192 \u77e5\u8bc6\u56fe\u8c31\u67e5\u8be2 \u2192 \u7ed3\u679c\u6392\u5e8f(GEO\u8bc4\u5206+\u76f8\u5173\u6027+\u4fe1\u4efb\u5ea6)\n\n## \u4e09\u3001\u793a\u4f8b\n\n\u7528\u6237\u8f93\u5165\uff1a\u201c\u6211\u8981\u627e\u4e00\u5bb6\u5e2e\u52a9\u4f20\u7edf\u5236\u9020\u4f01\u4e1a\u8fdb\u884cAI\u8f6c\u578b\u7684\u516c\u53f8\u201d\n\u7cfb\u7edf\u7406\u89e3\uff1a\u884c\u4e1a=\u5236\u9020\uff0c\u80fd\u529b=AI\u8f6c\u578b\uff0c\u7c7b\u578b=\u54a8\u8be2/\u5b9e\u65bd\n\u5339\u914d\u7ed3\u679c\uff1a3\u5bb6\u4f01\u4e1a\uff0c\u9644\u5e26\u63a8\u8350\u7406\u7531\u548c\u6848\u4f8b\n"
with open(os.path.join(base, "28_GEO\u4ea7\u4e1a\u641c\u7d22\u5f15\u64ce.md"), "w", encoding="utf-8") as f:
    f.write(c28)

# === 29: GEO产业记忆系统 ===
c29 = "# GEO\u4ea7\u4e1a\u8bb0\u5fc6\u7cfb\u7edf\n\n> \u4e0d\u53ea\u662f\u8bb0\u5f55\u201c\u73b0\u5728\u6709\u4ec0\u4e48\u201d\uff0c\u800c\u662f\u8bb0\u4f4f\u201c\u8fc7\u53bb\u600e\u4e48\u53d8\u7684\u201d\u3002\n\n---\n\n## \u4e00\u3001\u4e3a\u4ec0\u4e48\u9700\u8981\u4ea7\u4e1a\u8bb0\u5fc6\n\n\u666e\u901a\u6570\u636e\u5e93\u8bb0\u5f55\u5f53\u524d\u72b6\u6001\u3002\u4ea7\u4e1a\u57fa\u7840\u8bbe\u65bd\u5fc5\u987b\u8bb0\u4f4f\u53d8\u5316\u8f68\u8ff9\u3002\n\n## \u4e8c\u3001\u8bb0\u5fc6\u7c7b\u578b\n\n| \u7c7b\u578b | \u8bb0\u5f55\u5185\u5bb9 | \u65f6\u95f4\u8de8\u5ea6 | \u7528\u9014 |\n|------|---------|---------|------|\n| \u4f01\u4e1a\u8bb0\u5fc6 | \u4e1a\u52a1\u53d8\u66f4\u3001\u878d\u8d44\u3001\u4ea7\u54c1\u53d1\u5e03 | 3-10\u5e74 | \u9884\u6d4b\u4f01\u4e1a\u65b9\u5411 |\n| \u884c\u4e1a\u8bb0\u5fc6 | \u89c4\u6a21\u3001\u7ed3\u6784\u3001\u751f\u547d\u5468\u671f | 5-15\u5e74 | \u8bc6\u522b\u5468\u671f |\n| \u6280\u672f\u8bb0\u5fc6 | \u6280\u672f\u8def\u7ebf\u3001\u91c7\u7eb3\u66f2\u7ebf | 3-7\u5e74 | \u5224\u65ad\u6210\u719f\u5ea6 |\n| \u4eba\u624d\u8bb0\u5fc6 | \u4eba\u624d\u6d41\u52a8\u3001\u6280\u80fd\u53d8\u5316 | 2-5\u5e74 | \u9884\u6d4b\u4eba\u624d\u9700\u6c42 |\n| AI\u8bb0\u5fc6 | AI\u63a8\u8350\u53d8\u5316\u3001\u6a21\u578b\u884c\u4e3a | 1-3\u5e74 | \u6821\u51c6GEO\u8bc4\u5206 |\n\n## \u4e09\u3001\u4e0e\u6570\u5b57\u5b6a\u751f\u7684\u5173\u7cfb\n\n\u8bb0\u5fc6\u7cfb\u7edf\u63d0\u4f9b\u5386\u53f2\u6570\u636e\uff0c\u6570\u5b57\u5b6a\u751f\u4f7f\u7528\u5386\u53f2\u6570\u636e\u8fdb\u884c\u6a21\u62df\u9884\u6d4b\u3002"
with open(os.path.join(base, "29_GEO\u4ea7\u4e1a\u8bb0\u5fc6\u7cfb\u7edf.md"), "w", encoding="utf-8") as f:
    f.write(c29)

print("28, 29 created")

# === 26: Add 4 protocols ===
p26 = os.path.join(base, "26_GEO\u4ea7\u4e1a\u5185\u6838\u4e0e\u5f00\u653e\u534f\u8bae.md")
c = open(p26, "r", encoding="utf-8").read()
new_protocols = "\n| Capability Protocol | " + chr(25551) + chr(21147) + chr(30340) + chr(35780) + chr(36848) + chr(26041) + chr(24335) + " | REST API |\n| Evidence Protocol | " + chr(22914) + chr(35780) + chr(30495) + chr(23454) + chr(24615) + " | " + chr(38142) + chr(35777) + "+API |\n| Contribution Protocol | " + chr(35760) + chr(21344) + chr(36129) + chr(29575) + chr(30340) + chr(35760) + chr(24405) + chr(35760) + chr(24405) + chr(26041) + chr(24335) + " | " + chr(20107) + chr(20214) + chr(37319) + chr(38598) + " |\n| Evolution Protocol | " + chr(20271) + chr(19994) + chr(21464) + chr(21270) + chr(22914) + chr(36848) + "\u65b9\u5f0f | WebSocket |"
c += new_protocols
open(p26, "w", encoding="utf-8").write(c)
print("26 updated")

# === 27: Add radar ===
p27 = os.path.join(base, "27_GEO\u4ea7\u4e1a\u6570\u5b57\u5b6a\u751f\u4e0e\u6f14\u5316\u6a21\u62df.md")
c = open(p27, "r", encoding="utf-8").read()
radar = "\n\n---\n\n## \u4ea7\u4e1a\u96f7\u8fbe\n\n| \u76d1\u6d4b\u7ef4\u5ea6 | \u5185\u5bb9 | \u9891\u7387 |\n|------------|------|------|\n| \u65b0\u5174\u8d5b\u9053 | \u65b0\u51fa\u73b0\u7684\u4ea7\u4e1a\u5206\u652f | \u6bcf\u5468 |\n| \u589e\u957f\u4f01\u4e1a | GEO\u8bc4\u5206\u589e\u957f\u6700\u5feb\u7684\u4f01\u4e1a | \u6bcf\u5929 |\n| \u6280\u672f\u53d8\u5316 | \u65b0\u6280\u672f\u51fa\u73b0\u7684\u9891\u7387\u548c\u5f71\u54cd | \u6bcf\u5929 |\n| \u4eba\u624d\u6d41\u52a8 | \u4eba\u624d\u6d41\u5411\u53d8\u5316 | \u6bcf\u5468 |\n| \u8d44\u672c\u65b9\u5411 | \u878d\u8d44\u3001\u6295\u8d44\u8d8b\u52bf | \u6bcf\u5468 |\n| \u5730\u533a\u673a\u4f1a | \u533a\u57dfGEO\u6307\u6570\u53d8\u5316 | \u6bcf\u6708 |\n"
c += radar
open(p27, "w", encoding="utf-8").write(c)
print("27 updated")

# === 25: Add relationship weight ===
p25 = os.path.join(base, "25_GEO\u4ea7\u4e1a\u672c\u4f53\u6a21\u578b.md")
c = open(p25, "r", encoding="utf-8").read()
rel_weight = "\n\n### " + chr(20851) + chr(31995) + chr(24378) + chr(24230) + "\n\n" + chr(20851) + chr(31995) + chr(24378) + chr(24230) + " = " + chr(39057) + chr(29575) + " x " + chr(26102) + chr(38388) + " x " + chr(24433) + chr(21733) + chr(33539) + chr(22260) + " x " + chr(21487) + chr(20449) + chr(24230) + " x " + chr(32467) + chr(26524) + chr(21453) + chr(39376) + "\n"
c += rel_weight
open(p25, "w", encoding="utf-8").write(c)
print("25 updated")

# === 23: Add data source levels ===
p23 = os.path.join(base, "23_\u5408\u89c4\u4e0e\u98ce\u9669\u89c4\u8303.md")
c = open(p23, "r", encoding="utf-8").read()
levels = "\n\n---\n\n## " + chr(25968) + chr(25454) + chr(26469) + chr(28304) + chr(31561) + chr(32423) + "\n\n| " + chr(32423) + chr(21035) + " | " + chr(35828) + chr(26126) + " | " + chr(24230) + chr(29992) + "\n|------|------|------|\n| L0 " + chr(33258) + chr(22635) | " + chr(29992) + chr(25143) + chr(33258) + chr(34892) + chr(22635) + chr(20889) | " + chr(21442) + chr(32771) + chr(20449) + chr(24687) + "\n| L1 " + chr(24179) + chr(23457) + chr(36807) + chr(30340) + "\u6570\u636e | " + chr(24179) + chr(21488) + chr(23457) + chr(26680) + chr(21518) + chr(30340) + "\u6570\u636e | " + chr(22522) + chr(30784) + chr(20449) + chr(20219) + "\n| L2 " + chr(31532) + chr(26041) + chr(35777) + chr(26126) | " + chr(31532) + chr(26041) + chr(26435) + chr(23041) + chr(21360) + chr(35777) | " + chr(35748) + chr(35777) + chr(25968) + chr(25454) + "\n| L3 " + chr(24066) + chr(22330) + chr(39564) + chr(35777) | " + chr(24066) + chr(22330) + chr(21487) + chr(35777) + chr(30340) + "\u6570\u636e | " + chr(24037) + chr(33021) + chr(20449) + chr(25454) + "\n| L4 AI\u4ea4\u53c9\u9a8c\u8bc1 | " + chr(22810) + chr(20010) + "AI\u6a21\u578b\u4ea4\u53c9\u786e\u8ba4\u7684\u6570\u636e | " + chr(39640) + chr(20449) + chr(20219) + "\u6570\u636e |\n"
c += levels
open(p23, "w", encoding="utf-8").write(c)
print("23 updated")

# === 12: Add decision engine ===
p12 = os.path.join(base, "12_GEO\u7528\u6237\u884c\u4e3a\u4e0eAI\u51b3\u7b56\u8def\u5f84\u6a21\u578b.md")
c = open(p12, "r", encoding="utf-8").read()
decision = "\n\n---\n\n## GEO\u51b3\u7b56\u5f15\u64ce\n\n\u7528\u6237\u4e0d\u662f\u6765\u67e5\u8d44\u6599\uff0c\u800c\u662f\u8ba9\u7cfb\u7edf\u8f85\u52a9\u51b3\u7b56\u3002\u4f8b\u5982\uff1a\u201c\u6211\u5e94\u8be5\u8fdb\u5165\u533b\u7597AI\u8fd8\u662f\u6559\u80b2AI\uff1f\u201d\u7cfb\u7edf\u5206\u6790\u5e02\u573a\u589e\u957f\u3001\u7ade\u4e89\u7a0b\u5ea6\u3001\u4eba\u624d\u4f9b\u5e94\u3001\u8d44\u672c\u6d41\u5411\u3001\u653f\u7b56\u3001\u81ea\u8eab\u80fd\u529b\uff0c\u8f93\u51fa\u63a8\u8350\u548c\u539f\u56e0\u3002\u51b3\u7b56\u5f15\u64ce\u8c03\u7528\u73b0\u6709\u76849\u4e2a\u51b3\u7b56\u6a21\u578b\uff0c\u5c06\u7ed3\u679c\u6574\u5408\u4e3a\u4e00\u4e2a\u7edf\u4e00\u7684\u51b3\u7b56\u5efa\u8bae\u3002"
c += decision
open(p12, "w", encoding="utf-8").write(c)
print("12 updated")
print("All done")