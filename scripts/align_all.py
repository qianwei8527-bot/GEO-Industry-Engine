import os
base = "D:\\GEO-IE\\docs"

# 06: Insert infrastructure positioning after "### 6.1" header
p = os.path.join(base, "06_前端设计.md")
c = open(p, "r", encoding="utf-8").read()
marker = "### 6.1"
idx = c.find(marker)
if idx >= 0:
    eol = c.find("\n", idx)
    new_line = "\n\n> GEO\u4ea7\u4e1a\u57fa\u7840\u8bbe\u65bd\u5e73\u53f0: \u8ba9\u4f01\u4e1a\u6210\u4e3aAI\u641c\u7d22\u63a8\u8350\u9996\u9009\uff0c\u8ba9\u6bcf\u4e2a\u4eba\u627e\u5230\u81ea\u5df1\u7684\u4f4d\u7f6e\n"
    c = c[:eol+1] + new_line + c[eol+1:]
    open(p, "w", encoding="utf-8").write(c)
    print("06: done")
else:
    print("06: marker not found")

# 21: Broaden positioning from supplier listing to infrastructure
p = os.path.join(base, "21_应用场景设计.md")
c = open(p, "r", encoding="utf-8").read()
old = "GEO-Engine = AI\u65f6\u4ee3\u7684\u201c\u4f9b\u5e94\u5546\u4e0a\u699c\u7cfb\u7edf\u201d"
new = "GEO\u4ea7\u4e1a\u57fa\u7840\u8bbe\u65bd\u5e73\u53f0\uff1a\u8ba9\u4f01\u4e1a\u5728AI\u63a8\u8350\u4e2d\u627e\u5230\u81ea\u5df1\u7684\u4f4d\u7f6e\uff0c\u8ba9\u6bcf\u4e2a\u4e2a\u4f53\u5728\u4ea7\u4e1a\u4e2d\u53d1\u73b0\u6210\u957f\u8def\u5f84"
c = c.replace(old, new)
c = c.replace("\u4f9b\u5e94\u5546\u4e0a\u699c\u7cfb\u7edf", "\u4ea7\u4e1a\u57fa\u7840\u8bbe\u65bd\u5e73\u53f0")
c = c.replace("\u4f9b\u5e94\u5546\u63a8\u8350", "\u4ea7\u4e1a\u57fa\u7840\u8bbe\u65bd")
open(p, "w", encoding="utf-8").write(c)
print("21: done")

# 17: Add 5-layer product structure
p = os.path.join(base, "17_产品定义与商业模式.md")
c = open(p, "r", encoding="utf-8").read()
layers = "\n\n## \u4ea7\u54c1\u5c42\u7ea7\u7ed3\u6784\n\n| \u5c42\u7ea7 | \u4ea7\u54c1 | \u5b9a\u4f4d |\n|------|------|------|\n| \u5165\u53e3\u5c42 | GEO\u4f01\u4e1aAI\u53ef\u89c1\u5ea6\u8bca\u65ad(\u514d\u8d39) | \u7b2c\u4e00\u5165\u53e3 |\n| \u589e\u957f\u5c42 | AI\u53ef\u89c1\u5ea6SaaS(\u8ba2\u9605) | \u6301\u7eed\u670d\u52a1 |\n| \u751f\u6001\u5c42 | \u4ea7\u4e1a\u5730\u56fe+\u8ba4\u8bc1+\u4ea4\u6613 | \u8fde\u63a5\u4e0e\u4fe1\u4efb |\n| \u8d44\u4ea7\u5c42 | GEO\u6570\u636e\u8d44\u4ea7\u4e2d\u5fc3 | \u6570\u636e\u6c89\u6dc0\u4e0e\u667a\u80fd |\n| \u667a\u80fd\u5c42 | Agent OS(\u8fdc\u671f) | \u81ea\u52a8\u5316 |\n"
idx = c.find("## \u5546\u4e1a\u6a21\u5f0f")  # Find "## 商业模式"
if idx >= 0:
    c = c[:idx] + layers + "\n" + c[idx:]
    open(p, "w", encoding="utf-8").write(c)
    print("17: done")
else:
    print("17: marker not found")

# 24: Broaden MVP focus
p = os.path.join(base, "24_\u6267\u884c\u65b9\u6848\u4e0e90\u5929\u8ba1\u5212.md")
c = open(p, "r", encoding="utf-8").read()
old_target = "\u8ba9B2B\u4f9b\u5e94\u5546\u770b\u5230\u81ea\u5df1\u5728AI\u4e2d\u7684\u63a8\u8350\u60c5\u51b5"
new_target = "\u8ba9\u4f01\u4e1a\u770b\u5230\u81ea\u5df1\u5728AI\u4e2d\u7684\u63a8\u8350\u60c5\u51b5\uff0c\u901a\u8fc7\u514d\u8d39\u8bca\u65ad\u83b7\u53d6\u53ef\u89c1\u5ea6\u5206\u6570\u548c\u4f18\u5316\u5efa\u8bae"
if old_target in c:
    c = c.replace(old_target, new_target)
    open(p, "w", encoding="utf-8").write(c)
    print("24: done")
else:
    print("24: target not found")