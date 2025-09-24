export default defineNuxtConfig({
  css: ['@/assets/css/tailwind.css'],

  postcss: {
    plugins: {
      '@tailwindcss/postcss': {},  // 
      autoprefixer: {}
    }
  },

  compatibilityDate: '2025-09-23',
  modules: ['@pinia/nuxt'],
  pages: true,
  runtimeConfig: {
    public: {
      apiBaseUrl: process.env.NUXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000/api',
      adminApiKey: process.env.NUXT_PUBLIC_ADMIN_API_KEY || ''
    }
  },
  app: {
    head: {
      title: 'Sorteo San Valentín',
      meta: [{ name: 'viewport', content: 'width=device-width, initial-scale=1' }]
    }
  }
})
