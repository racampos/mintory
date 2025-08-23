/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  env: {
    // Server-side environment variables for API routes
    BACKEND_URL: process.env.BACKEND_URL || 'http://localhost:8000',
    MCP_URL: process.env.MCP_URL || 'http://localhost:3001',
    
    // Client-side environment variables  
    NEXT_PUBLIC_CHAIN_ID: process.env.NEXT_PUBLIC_CHAIN_ID || '360',
  },
}

module.exports = nextConfig
