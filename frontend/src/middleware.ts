import { NextResponse, type NextRequest } from "next/server";

const REDIRECTS: Array<{ prefix: string; to: string }> = [
  { prefix: "/intelligence/risks", to: "/governance" },
  { prefix: "/intelligence/competitors", to: "/detection" },
  { prefix: "/intelligence/opportunities", to: "/operations" },
  { prefix: "/intelligence", to: "/operations" },
  { prefix: "/certification", to: "/governance" },
  { prefix: "/assets", to: "/realm" },
  { prefix: "/identity", to: "/realm" },
  { prefix: "/marketplace", to: "/market" },
  { prefix: "/universe/3d", to: "/navigation" },
  { prefix: "/universe/connections", to: "/navigation" },
  { prefix: "/universe/growth", to: "/navigation" },
  { prefix: "/universe/home", to: "/navigation" },
  { prefix: "/universe/join", to: "/navigation" },
  { prefix: "/universe/opportunities", to: "/navigation" },
  { prefix: "/universe/trust", to: "/navigation" },
  { prefix: "/admin", to: "/operations" },
];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const match = REDIRECTS.find(
    (item) => pathname === item.prefix || pathname.startsWith(`${item.prefix}/`),
  );
  if (match) {
    return NextResponse.redirect(new URL(match.to, request.url));
  }
  return NextResponse.next();
}

export const config = {
  matcher: [
    "/intelligence/:path*",
    "/certification/:path*",
    "/assets/:path*",
    "/identity/:path*",
    "/marketplace/:path*",
    "/universe/3d/:path*",
    "/universe/connections/:path*",
    "/universe/growth/:path*",
    "/universe/home/:path*",
    "/universe/join/:path*",
    "/universe/opportunities/:path*",
    "/universe/trust/:path*",
    "/admin/:path*",
  ],
};
