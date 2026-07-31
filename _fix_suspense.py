# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")

with open(r"D:\GEO-Industry-Engine\frontend\src\app\navigation\page.tsx", "r", encoding="utf-8") as f:
    text = f.read()

# Add Suspense import
old_import = "import { useState, useEffect, useRef, useCallback } from \"react\";"
new_import = "import { useState, useEffect, useRef, useCallback, Suspense } from \"react\";"
text = text.replace(old_import, new_import)

# Find the function declaration and wrap
old_fn = "export default function NavigationPage() {"
new_fn = "function NavigationPage() {"
text = text.replace(old_fn, new_fn)

# Find the end of the file and add the wrapper
# The file ends with the closing brace of NavigationPage plus perhaps an empty line
# Add a new default export that wraps in Suspense
old_end = "  );\n}"
new_end = "  );\n}\n\n// Wrap in Suspense for useSearchParams (Next.js App Router requirement)\nexport default function Page() {\n  return (\n    <Suspense fallback={<div className=\"flex items-center justify-center min-h-[70vh]\"><div className=\"text-center\"><div className=\"w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4\"></div><p className=\"text-slate-500 text-lg\">Loading GEO Universe...</p></div></div>}>\n      <NavigationPage />\n    </Suspense>\n  );\n}"

if old_end in text:
    text = text.replace(old_end, new_end)
    with open(r"D:\GEO-Industry-Engine\frontend\src\app\navigation\page.tsx", "w", encoding="utf-8") as f:
        f.write(text)
    print("OK: Suspense wrapper added")
else:
    print("ERROR: old_end not found")
    # Find what the file ends with
    lines = text.split("\n")
    for i in range(len(lines)-5, len(lines)):
        print(f"  {i}: {lines[i][:100]}")
