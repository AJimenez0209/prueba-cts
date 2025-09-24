<template>
  <div class="mx-auto max-w-xl p-6 space-y-6">
    <header class="space-y-1">
      <h1 class="text-2xl font-semibold">Sorteo</h1>
      <p class="text-sm text-gray-500">Selecciona aleatoriamente un ganador y notifica por correo.</p>
    </header>

    <!-- Estados -->
    <div v-if="errorMsg" class="rounded-md border border-red-300 bg-red-50 p-3 text-red-800">
      {{ errorMsg }}
    </div>
    <div v-if="successMsg" class="rounded-md border border-green-300 bg-green-50 p-3 text-green-800">
      {{ successMsg }}
    </div>

    <!-- Acción -->
    <button @click="onDraw" :disabled="loading"
            class="rounded-md bg-black px-4 py-2 text-white disabled:opacity-60">
      <span v-if="!loading">Sortear ganador</span>
      <span v-else>Ejecutando sorteo…</span>
    </button>

    <!-- Resultado -->
    <section v-if="winner" class="rounded-md border p-4">
      <h2 class="font-semibold mb-2">Ganador</h2>
      <p><strong>Nombre:</strong> {{ winner.full_name }}</p>
      <p><strong>Email:</strong> {{ winner.email }}</p>
      <p class="text-xs text-gray-500 mt-2">
        {{ detail }}
      </p>
    </section>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: ['require-admin'] })

import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useApi } from '~/composables/useApi'

const api = useApi()
const router = useRouter()

const loading = ref(false)
const errorMsg = ref<string | null>(null)
const successMsg = ref<string | null>(null)

const winner = ref<any | null>(null)
const detail = ref<string>('')

async function onDraw() {
  errorMsg.value = null
  successMsg.value = null
  winner.value = null
  detail.value = ''
  loading.value = true

  try {
    const res = await api('/admin/draw/', {
      method: 'POST'
    }) as { winner: any; detail: string; task_id?: string }

    winner.value = res?.winner || null
    detail.value = res?.detail || ''
    // Confirmación requerida por enunciado (notificación encolada)
    successMsg.value = 'Ganador seleccionado y notificado por correo (tarea Celery encolada).'
  } catch (err: any) {
    const status = err?.status || err?.response?.status
    if (status === 401) {
      return router.push('/admin/login')
    }
    errorMsg.value = err?.data?.detail || err?.data?.message || 'No se pudo ejecutar el sorteo.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.text-gray-500 { color: #6b7280; }
.rounded-md { border-radius: 0.375rem; }
.border { border: 1px solid #e5e7eb; }
.p-4 { padding: 1rem; }
.p-6 { padding: 1.5rem; }
.mx-auto { margin-left: auto; margin-right: auto; }
.max-w-xl { max-width: 36rem; }
.bg-black { background: #000; }
.text-white { color: #fff; }
</style>
