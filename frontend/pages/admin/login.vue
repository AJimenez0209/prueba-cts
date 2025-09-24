<template>
    <div class="mx-auto max-w-md p-6 space-y-6">
        <header class="space-y-1">
            <h1 class="text-2xl font-semibold">Login Administrador</h1>
            <p class="text-sm text-gray-500">Ingresa la API Key para acceder al panel.</p>
        </header>

        <div v-if="errorMsg" class="rounded-md border border-red-300 bg-red-50 p-3 text-red-800">
            {{ errorMsg }}
        </div>

        <form @submit.prevent="onLogin" class="space-y-4">
            <div>
                <label class="block text-sm font-medium mb-1">API Key</label>
                <input v-model.trim="apiKey" type="text" class="w-full rounded-md border p-2"
                    placeholder="Ingresa tu clave de administrador" />
            </div>

            <button type="submit" class="rounded-md bg-black px-4 py-2 text-white disabled:opacity-60"
                :disabled="loading">
                <span v-if="!loading">Entrar</span>
                <span v-else>Entrando…</span>
            </button>
        </form>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAdminStore } from '~/stores/admin'

const route = useRoute()
const router = useRouter()
const adminStore = useAdminStore()

const apiKey = ref('')
const loading = ref(false)
const errorMsg = ref<string | null>(null)

async function onLogin() {
  errorMsg.value = null
  loading.value = true
  try {
    if (!apiKey.value) throw new Error('Debes ingresar una API Key')
    adminStore.setKey
      ? adminStore.setKey(apiKey.value)
      : (adminStore as any).setKey?.(apiKey.value) // por si tu store usa setKey

    const redirect = typeof route.query.redirect === 'string'
      ? route.query.redirect
      : '/admin/participants'

    router.replace(redirect) // 👈 vuelve a donde querías ir
  } catch (err: any) {
    errorMsg.value = err?.message || 'Error en login'
  } finally {
    loading.value = false
  }
}
</script>


<style scoped>
.text-gray-500 {
    color: #6b7280;
}

.rounded-md {
    border-radius: 0.375rem;
}

.border {
    border: 1px solid #e5e7eb;
}

.p-2 {
    padding: 0.5rem;
}

.p-6 {
    padding: 1.5rem;
}

.max-w-md {
    max-width: 28rem;
}

.mx-auto {
    margin-left: auto;
    margin-right: auto;
}

.bg-black {
    background: #000;
}

.text-white {
    color: #fff;
}
</style>
