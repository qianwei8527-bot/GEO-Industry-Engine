import os

# Fix 21: reposition the title
p = os.path.join("D:\\GEO-IE", "docs", "21_应用场景设计.md")
c = open(p, "r", encoding="utf-8").read()

# Find "### 1.1" (pure ASCII) and replace the description
idx = c.find("### 1.1")
if idx >= 0:
    eol = c.find("\n", idx)
    # Replace the line with new positioning
    new_header = "### 1.1 GEO\u4ea7\u4e1a\u57fa\u7840\u8bbe\u65bd\u5e73\u53f0\uff1a\u8ba9\u6bcf\u4e2a\u4f01\u4e1a\u627e\u5230\u81ea\u5df1\u5728AI\u63a8\u8350\u4e2d\u7684\u4f4d\u7f6e"
    c = c[:idx] + new_header + c[eol:]
    print("21: header replaced")
else:
    print("21: marker not found")

# Replace "供应商上榜系统" with ASCII-based position
old = "GEO-Engine = AI\u65f6\u4ee3\u7684\u201c\u4f9b\u5e94\u5546\u4e0a\u699c\u7cfb\u7edf\u201d"
new = "GEO\u4ea7\u4e1a\u57fa\u7840\u8bbe\u65bd\u5e73\u53f0"
idx = c.find(old[:20])
if idx >= 0 and c[idx:idx+len(old)] == old:
    c = c[:idx] + new + c[idx+len(old):]
    print("21: old text replaced")
c = c.replace("\u4f9b\u5e94\u5546\u4e0a\u699c\u7cfb\u7edf", "\u4ea7\u4e1a\u57fa\u7840\u8bbe\u65bd")
open(p, "w", encoding="utf-8").write(c)
print("21: done")

# Fix 24: broaden MVP focus
p = os.path.join("D:\\GEO-IE", "docs", "24_执行方案与90天计划.md")
c = open(p, "r", encoding="utf-8").read()

# Find "B2B" in context
idx = c.find("B2B\u4f9b\u5e94\u5546")  # B2B供应商
if idx >= 0:
    # Find the end of the bold text
    end_marker = c.find("\n", idx)
    if end_marker > 0:
        new_target = "\u4f01\u4e1a\u770b\u5230\u81ea\u5df1\u5728AI\u4e2d\u7684\u63a8\u8350\u60c5\u51b5\uff0c\u901a\u8fc7\u514d\u8d39\u8bca\u65ad\u83b7\u53d6\u53ef\u89c1\u5ea6\u5206\u6570\u548c\u4f18\u5316\u5efa\u8bae"
        c = c[:idx] + new_target + c[idx + len("B2B\u4f9b\u5e94\u5546\u770b\u5230\u81ea\u5df1\u5728AI\u4e2d\u7684\u63a8\u8350\u60c5\u51b5"):]
        open(p, "w", encoding="utf-8").write(c)
        print("24: done")
    else:
        print("24: end not found")
else:
    print("24: B2B not found")