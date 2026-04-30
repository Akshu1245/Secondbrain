/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // When NEXT_PUBLIC_API_BASE_URL is set (production / static export), the
  // frontend talks directly to the absolute backend URL, so we can ship a
  // pure-static build. Otherwise we fall back to dev rewrites.
  ...(process.env.STATIC_EXPORT === "1"
    ? { output: "export", trailingSlash: true, images: { unoptimized: true } }
    : {
        async rewrites() {
          const base = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8001";
          return [{ source: "/api/:path*", destination: `${base}/api/:path*` }];
        },
      }),
};
export default nextConfig;
