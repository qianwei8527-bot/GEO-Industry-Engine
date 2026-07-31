import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "GEO Universe - 产业认知与连接基础设施",
  description: "每一个节点，都是自身宇宙的中心。",
};

export default function UniverseLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
