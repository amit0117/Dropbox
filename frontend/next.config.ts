import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Redirect trailing-slash URLs to no-slash so Origin header matches backend CORS allowlist
  trailingSlash: false,
};

export default nextConfig;
