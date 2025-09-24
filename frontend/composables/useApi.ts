// composables/useApi.ts
import { ofetch } from 'ofetch'
import { useRuntimeConfig } from 'nuxt/app'
import { useAdminStore } from '../stores/admin'

// Crea una instancia de ofetch con la configuración base y la lógica para añadir la API Key en las rutas admin
export const useApi = () => {
  const config = useRuntimeConfig()
  const baseURL = String(config.public.apiBaseUrl)
  const adminStore = useAdminStore()

  const api = ofetch.create({
    baseURL,
    onRequest({ options, request }) {
      try {
        const url = typeof request === 'string'
          ? request
          : (request as any).url

        // Solo para rutas admin
        if (url.startsWith('/admin/') || url.includes('/admin/')) {
          const apiKey = adminStore.apiKey || config.public.adminApiKey
          if (apiKey) {
            // Normalizamos a Headers y seteamos la cabecera de forma tipada
            const h = new Headers(options.headers as HeadersInit | undefined)
            h.set('X-API-Key', String(apiKey))
            options.headers = h
          }
        }
      } catch {
        /* noop */
      }
    }
  })

  return api
}
