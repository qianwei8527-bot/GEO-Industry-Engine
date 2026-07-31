export default function HomePage() {
  return (
    <div style={{ minHeight: "100vh", background: "#0f172a", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div style={{ textAlign: "center" }}>
        <h1 style={{ color: "#fff", fontSize: "2rem", fontWeight: "bold" }}>GEO Universe</h1>
        <p style={{ color: "#94a3b8", marginTop: "1rem" }}>产业认知与连接基础设施</p>
        <a href="/universe/navigation" style={{ display: "inline-block", marginTop: "2rem", padding: "0.75rem 1.5rem", background: "#3b82f6", color: "#fff", borderRadius: "0.5rem", textDecoration: "none" }}>
          进入宇宙
        </a>
      </div>
    </div>
  );
}
