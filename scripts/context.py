import os
base = "D:\\GEO-IE\\docs"

# === 00: Add Context Layer positioning ===
p00 = os.path.join(base, "00_\u9879\u76ee\u5baa\u7ae0.md")
c = open(p00, "r", encoding="utf-8").read()
context_line = "\n\n> \u672c\u8d28\u4e0a\uff0cGEO-Industry-Engine\u662fAI\u65f6\u4ee3\u8fde\u63a5\u4eba\u5de5\u667a\u80fd\u4e0e\u771f\u5b9e\u4ea7\u4e1a\u4e16\u754c\u7684\u884c\u4e1a\u4e0a\u4e0b\u6587\u5c42\u3002"
c = c.replace("> \u4e00\u4e2a\u5f00\u653e\u7684GEO", context_line + "\n\n> \u4e00\u4e2a\u5f00\u653e\u7684GEO")
open(p00, "w", encoding="utf-8").write(c)
print("00 done")

# === 26: Add MCP Server protocol ===
p26 = os.path.join(base, "26_GEO\u4ea7\u4e1a\u5185\u6838\u4e0e\u5f00\u653e\u534f\u8bae.md")
c = open(p26, "r", encoding="utf-8").read()
mcp_line = "| GEO MCP Server | AI Agent\u901a\u8fc7Model Context Protocol\u8bbf\u95eeGEO\u4ea7\u4e1a\u6570\u636e | MCP\u534f\u8bae |"
c = c.replace("| Evolution Protocol", mcp_line + "\n" + "| Evolution Protocol")
open(p26, "w", encoding="utf-8").write(c)
print("26 done")
print("All done")