// middleware/require-admin.ts
import { defineNuxtRouteMiddleware, navigateTo } from 'nuxt/app'
import { useAdminStore } from '../stores/admin'


export default defineNuxtRouteMiddleware((to) => {
  const admin = useAdminStore()
  if (!admin?.apiKey) {
    // guarda la ruta a la que el user quería entrar
    const redirect = encodeURIComponent(to.fullPath || '/admin/participants')
    return navigateTo(`/admin/login?redirect=${redirect}`)
  }
})
