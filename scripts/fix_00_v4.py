import os
p = os.path.join("D:\\GEO-IE", "docs", "00_项目宪章.md")
c = open(p, "r", encoding="utf-8").read()
lines = c.splitlines()
prefix = 'GEO-Engine = AI' + chr(0x65f6) + chr(0x4ee3) + chr(0x7684) + chr(0x4f9b) + chr(0x5e94) + chr(0x5546) + chr(0x4e0a) + chr(0x699c) + chr(0x7cfb) + chr(0x7edf) + chr(0x3002)
# Lines: 0=title, 1=blank, 2=subtitle, 3=blank, 4=blockquote
lines[4] = '> ' + prefix + lines[4][2:]
open(p, "w", encoding="utf-8").write('\n'.join(lines))
c2 = open(p, "r", encoding="utf-8").read()
print("GEO-Engine:", "GEO-Engine" in c2)
print("bytes:", os.path.getsize(p))
