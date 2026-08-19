/** @type {import("next").NextConfig} */
const nextConfig = {
  images: { domains: ["localhost"] },
  async rewrites() {
    return [
      { source: "/api/v1/:path*", destination: "http://localhost:8080/api/v1/:path*" },
      { source: "/v106-all-pages-design-preview.html", destination: "/v106-all-pages-design-preview" },
    ];
  },
};

module.exports = nextConfig;
