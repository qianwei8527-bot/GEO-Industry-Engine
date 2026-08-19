import { readFile } from "node:fs/promises";
import path from "node:path";
import PanoramaExplorer from "@/components/panorama/panorama-explorer";
import type { PanoramaCapabilityMap, PanoramaFixtureRegistry, PanoramaRegistry } from "@/lib/panorama/types";

async function loadJson<T>(relative: string): Promise<T> {
  const file = path.resolve(process.cwd(), "..", "config", "panorama", relative);
  return JSON.parse(await readFile(file, "utf8")) as T;
}

export default async function PanoramaPage() {
  const [registry, fixtures, capabilityMap] = await Promise.all([
    loadJson<PanoramaRegistry>("page-registry.json"),
    loadJson<PanoramaFixtureRegistry>("fixture-registry.json"),
    loadJson<PanoramaCapabilityMap>("capability-map.json"),
  ]);
  return <PanoramaExplorer registry={registry} fixtures={fixtures} capabilityMap={capabilityMap} />;
}
