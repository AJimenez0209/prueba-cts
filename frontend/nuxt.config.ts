export default defineNuxtConfig({
  compatibilityDate: '2025-09-23',
  modules: ['@pinia/nuxt'],
  pages: true,                 
  runtimeConfig: {
    public: {
      apiBaseUrl: process.env.NUXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000/api',
      adminApiKey: process.env.NUXT_PUBLIC_ADMIN_API_KEY || ''
    }
  }
})
