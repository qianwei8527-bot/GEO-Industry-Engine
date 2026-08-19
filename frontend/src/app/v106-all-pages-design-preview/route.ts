import { readFile } from "node:fs/promises";
import path from "node:path";
import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function GET() {
  const preview = path.resolve(process.cwd(), "..", "docs", "v106-all-pages-design-preview.html");
  const html = await readFile(preview, "utf8");
  return new NextResponse(html, {
    headers: {
      "content-type": "text/html; charset=utf-8",
      "cache-control": "no-store",
    },
  });
}
