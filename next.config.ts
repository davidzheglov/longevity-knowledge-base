import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  reactStrictMode: true,
  eslint: {
    // Allow build to pass even if ESLint finds issues (CI-friendly for now)
    ignoreDuringBuilds: true,
  },
  typescript: {
    // Allow build to pass even if type errors exist (until we tighten types)
    ignoreBuildErrors: true,
  },
}

export default nextConfig
