// stores/admin.ts
import { defineStore } from 'pinia'
import { isClient } from '@vueuse/core'

// Store para gestionar la API Key del admin y persistirla en localStorage
export const useAdminStore = defineStore('admin', {
  state: () => ({
    apiKey: isClient ? (localStorage.getItem('ADMIN_API_KEY') || '') : ''
  }),
  actions: {
    setKey(key: string) {
      this.apiKey = key
      if (isClient) localStorage.setItem('ADMIN_API_KEY', key)
    },
    clear() {
      this.apiKey = ''
      if (isClient) localStorage.removeItem('ADMIN_API_KEY')
    }
  },
  getters: {
    hasKey: (s) => !!s.apiKey
  }
})
