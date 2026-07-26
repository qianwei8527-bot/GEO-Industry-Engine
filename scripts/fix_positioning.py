import os

# Fix 00: add B2B positioning
p00 = os.path.join("D:\\GEO-IE", "docs", "00_项目宪章.md")
c = open(p00, "r", encoding="utf-8").read()

# Add the B2B supplier listing positioning
old = "构建企业在AI世界中的定位、认知、信任、推荐和交易基础设施。"
new = "GEO-Engine = AI时代的供应商上榜系统。构建企业在AI世界中的定位、认知、信任、推荐和交易基础设施。"
c = c.replace(old, new)
open(p00, "w", encoding="utf-8").write(c)
print("00 fixed: " + str(os.path.getsize(p00)) + " bytes")

# Fix README: update doc count
pr = os.path.join("D:\\GEO-IE", "README.md")
c = open(pr, "r", encoding="utf-8").read()
c = c.replace("21份架构文档", "22份架构文档")
c = c.replace("├── docs/           # 21份架构文档", "├── docs/           # 22份架构文档")
open(pr, "w", encoding="utf-8").write(c)
print("README fixed")