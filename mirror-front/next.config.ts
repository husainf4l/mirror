import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Allow cross-origin requests from raheva.com in development
  allowedDevOrigins: ['raheva.com', 'www.raheva.com'],
  
  // Optimize performance for LiveKit media streaming
  experimental: {
    optimizePackageImports: ['@livekit/components-react'],
  },
  
  // Configure headers for LiveKit WebRTC
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin',
          },
        ],
      },
    ];
  },

  // Enable compression
  compress: true,
  
  // Power performance optimizations
  poweredByHeader: false,
  
  // Image optimization
  images: {
    formats: ['image/webp', 'image/avif'],
  },
};

export default nextConfig;
