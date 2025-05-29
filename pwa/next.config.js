/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Future PWA configuration might go here
  // For example, using a plugin like @ducanh2912/next-pwa
  // pwa: {
  //   dest: 'public',
  //   register: true,
  //   skipWaiting: true,
  // },

  // Add rewrites for API proxying to FastAPI backends
  async rewrites() {
    return [
      // LLM Configuration Service (Model Management) - Port 45311
      {
        source: '/api/system/:path*',
        destination: 'http://127.0.0.1:45311/api/system/:path*',  // System resources
      },
      {
        source: '/api/gemma-models/:path*',
        destination: 'http://127.0.0.1:45311/api/gemma-models/:path*',  // Gemma models
      },
      {
        source: '/api/llm-services/:path*',
        destination: 'http://127.0.0.1:45311/api/llm-services/:path*',  // LLM services
      },
      {
        source: '/api/guidance/:path*',
        destination: 'http://127.0.0.1:45311/api/guidance/:path*',  // Guidance operations
      },
      {
        source: '/api/lmql/:path*',
        destination: 'http://127.0.0.1:45311/api/lmql/:path*',  // LMQL operations
      },
      {
        source: '/api/llm-config/:path*',
        destination: 'http://127.0.0.1:45311/api/llm-config/:path*',  // LLM config health
      },

      // Main Translation Backend - Port 8000
      {
        source: '/api/translate',
        destination: 'http://127.0.0.1:8000/api/translate',  // Translation endpoint
      },
      {
        source: '/api/providers/:path*',
        destination: 'http://127.0.0.1:8000/api/providers/:path*',  // Provider management
      },
      {
        source: '/auth',
        destination: 'http://127.0.0.1:8000/auth',  // Authentication endpoint
      },
      {
        source: '/health',
        destination: 'http://127.0.0.1:8000/health',  // Main backend health check
      },
    ];
  },
};

module.exports = nextConfig;
