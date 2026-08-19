export default function HomePage() {
  return (
    <div style={{ minHeight: "100vh", background: "#0f172a", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "space-between", padding: "3rem 1rem" }}>
      <div style={{ textAlign: "center", flex: 1, display: "flex", flexDirection: "column", justifyContent: "center" }}>
        <h1 style={{ color: "#fff", fontSize: "2rem", fontWeight: "bold" }}>恒域世界</h1>
        <p style={{ color: "#94a3b8", marginTop: "1rem" }}>让每个域主，拥有自己的产业世界</p>
        <div style={{ marginTop: "2rem", display: "flex", gap: "0.75rem", justifyContent: "center", flexWrap: "wrap" }}>
          <a href="/login" style={{ display: "inline-block", padding: "0.75rem 1.5rem", background: "#3b82f6", color: "#fff", borderRadius: "0.5rem", textDecoration: "none" }}>
            登录
          </a>
          <a href="/register" style={{ display: "inline-block", padding: "0.75rem 1.5rem", border: "1px solid #334155", color: "#e2e8f0", borderRadius: "0.5rem", textDecoration: "none" }}>
            注册
          </a>
          <a href="/navigation" style={{ display: "inline-block", padding: "0.75rem 1.5rem", border: "1px solid #334155", color: "#e2e8f0", borderRadius: "0.5rem", textDecoration: "none" }}>
            进入宇宙
          </a>
        </div>
      </div>
      <div style={{ textAlign: "center", paddingTop: "2rem", width: "100%", maxWidth: "560px" }}>
        <div style={{ color: "#e2e8f0", fontSize: "1.15rem", fontWeight: 700, marginBottom: "0.75rem" }}>检测中心</div>
        <form action="/detection" method="get" style={{ display: "flex", gap: "0.5rem" }}>
          <input
            name="query"
            placeholder="输入品牌、企业或网址开始检测"
            style={{ flex: 1, padding: "0.75rem 1rem", borderRadius: "0.5rem", border: "1px solid #334155", background: "#0f172a", color: "#fff", outline: "none" }}
          />
          <button type="submit" style={{ padding: "0.75rem 1.25rem", borderRadius: "0.5rem", background: "#3b82f6", color: "#fff", border: "none", fontWeight: 600, cursor: "pointer" }}>
            开始检测
          </button>
        </form>
      </div>
    </div>
  );
}
