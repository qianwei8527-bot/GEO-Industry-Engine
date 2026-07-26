import re, os
p = os.path.join("D:\\GEO-IE", "docs", "00_项目宪章.md")
c = open(p, "r", encoding="utf-8").read()
prefix = 'GEO-Engine = AI\u65f6\u4ee3\u7684\u4f9b\u5e94\u5546\u4e0a\u699c\u7cfb\u7edf\u3002'
c = re.sub(r'^> .*\u57fa\u7840\u8bbe\u65bd\u3002$', lambda m: '> ' + prefix + m.group(0)[2:], c, flags=re.MULTILINE)
open(p, "w", encoding="utf-8").write(c)
c2 = open(p, "r", encoding="utf-8").read()
print("供应商上榜系统:", "供应商上榜系统" in c2)
print("文件大小:", os.path.getsize(p))
