import os
p00 = os.path.join("D:\\GEO-IE", "docs", "00_项目宪章.md")
c = open(p00, "r", encoding="utf-8").read()

# Fix 1: Replace positioning - find exact text from file
idx = c.find("GEO-Engine = AI")
if idx >= 0:
    old_core = c[idx:idx+80]  # Read the exact text
    new_core = "GEO\u4ea7\u4e1a\u57fa\u7840\u8bbe\u65bd\u5e73\u53f0\u3002\u6bcf\u4e2a\u4eba\u90fd\u80fd\u5728\u8fd9\u91cc\u627e\u5230\u81ea\u5df1\u7684\u4f4d\u7f6e"
    c = c.replace(old_core, new_core, 1)
    print("Fix 1: replaced positioning")
else:
    print("Fix 1: marker not found")

# Fix 2: Replace product structure - find "### \u8bc4\u5206\u7b97\u6cd5"
old_sys = "### \u8bc4\u5206\u7b97\u6cd5"
new_sys = """### \u4ea7\u54c1\u5c42\u7ea7\u7ed3\u6784

| \u5c42\u7ea7 | \u4ea7\u54c1 | \u5b9a\u4f4d |
|------|------|------|
| \u5165\u53e3\u5c42 | GEO\u4f01\u4e1aAI\u53ef\u89c1\u5ea6\u8bca\u65ad(\u514d\u8d39) | \u7b2c\u4e00\u5165\u53e3 |
| \u589e\u957f\u5c42 | AI\u53ef\u89c1\u5ea6SaaS(\u8ba2\u9605) | \u6301\u7eed\u670d\u52a1 |
| \u751f\u6001\u5c42 | \u4ea7\u4e1a\u5730\u56fe+\u8ba4\u8bc1+\u4ea4\u6613 | \u8fde\u63a5\u4e0e\u4fe1\u4efb |
| \u8d44\u4ea7\u5c42 | GEO\u6570\u636e\u8d44\u4ea7\u4e2d\u5fc3 | \u6570\u636e\u6c89\u6dc0 |
| \u667a\u80fd\u5c42 | Agent OS(\u8fdc\u671f) | \u81ea\u52a8\u5316 |

### \u8bc4\u5206\u7b97\u6cd5"""

if old_sys in c:
    c = c.replace(old_sys, new_sys, 1)
    print("Fix 2: replaced product structure")
else:
    print("Fix 2: marker not found")

open(p00, "w", encoding="utf-8").write(c)
print("Done")