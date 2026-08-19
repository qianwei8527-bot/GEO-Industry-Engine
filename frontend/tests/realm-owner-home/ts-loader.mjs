import { existsSync } from "node:fs";
import { fileURLToPath, pathToFileURL } from "node:url";
import path from "node:path";

const EXTENSIONS = [".ts", ".tsx", ".js", ".mjs"];

export async function resolve(specifier, context, nextResolve) {
  if (specifier.startsWith(".") && !/\.[a-zA-Z0-9]+$/.test(specifier)) {
    const parent = context.parentURL ? fileURLToPath(context.parentURL) : process.cwd();
    const base = path.resolve(path.dirname(parent), specifier);
    for (const ext of EXTENSIONS) {
      const candidate = base + ext;
      if (existsSync(candidate)) {
        return nextResolve(pathToFileURL(candidate).href, context);
      }
    }
  }
  return nextResolve(specifier, context);
}