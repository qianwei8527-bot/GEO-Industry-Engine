import os
p = os.path.join("D:\\GEO-IE", "docs", "00_项目宪章.md")
c = open(p, "r", encoding="utf-8").read()
lines = c.split(chr(10))
prefix = cast = prefix = 'GEO-Engine = AI' + chr(0x65f6) + chr(0x4ee3) + chr(0x7684) + chr(0x4f9b) + chr(0x5e94) + chr(0x5546) + chr(0x4e0a) + chr(0x699c) + chr(0x7cfb) + chr(0x7edf) + chr(0x3002)
match = chr(0x57fa) + chr(0x7840) + chr(0x8bbe) + chr(0x65bd) + chr(0x3002)
for i, line in enumerate(lines):
    if match in line and line.startswith('> '):
        lines[i] = '> ' + prefix + line[2:]
        break
open(p, "w", encoding="utf-8").write(chr(10).join(lines))
c2 = open(p, "r", encoding="utf-8").read()
print("供应商上榜系统:", "供应商上榜系统" in c2)
