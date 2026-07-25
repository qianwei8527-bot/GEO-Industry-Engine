import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "GEO-Industry-Engine",
  description: "AI时代企业增长基础设施 | GEO产业导航与交易平台",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body className="min-h-screen bg-white">{children}</body>
    </html>
  );
}
