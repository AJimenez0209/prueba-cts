<!-- pages/index.vue -->
<template>
  <div class="mx-auto max-w-xl p-6 space-y-6">
    <header class="space-y-1">
      <h1 class="text-2xl font-semibold">Inscripción al sorteo</h1>
      <p class="text-sm text-gray-500">Completa tus datos para participar.</p>
    </header>

    <!-- Alerts -->
    <div v-if="successMsg" class="rounded-md border border-green-300 bg-green-50 p-3 text-green-800">
      {{ successMsg }}
    </div>
    <div v-if="errorMsg" class="rounded-md border border-red-300 bg-red-50 p-3 text-red-800">
      {{ errorMsg }}
    </div>

    <form @submit.prevent="onSubmit" class="space-y-4">
      <div>
        <label class="block text-sm font-medium mb-1">Nombre completo</label>
        <input v-model.trim="form.full_name" type="text" class="w-full rounded-md border p-2"
               :class="{'border-red-400': submitted && !form.full_name}" placeholder="Ana Pérez" />
        <p v-if="submitted && !form.full_name" class="text-xs text-red-600 mt-1">Este campo es requerido.</p>
      </div>

      <div>
        <label class="block text-sm font-medium mb-1">Email</label>
        <input v-model.trim="form.email" type="email" class="w-full rounded-md border p-2"
               :class="{'border-red-400': submitted && !isEmailValid}" placeholder="ana@example.com" />
        <p v-if="submitted && !isEmailValid" class="text-xs text-red-600 mt-1">Ingresa un email válido.</p>
      </div>

      <div>
        <label class="block text-sm font-medium mb-1">Teléfono</label>
        <input v-model.trim="form.phone" type="text" class="w-full rounded-md border p-2"
               placeholder="+56 9 1234 5678" />
        <p v-if="submitted && !form.phone" class="text-xs text-red-600 mt-1">Este campo es requerido.</p>
      </div>

      <button type="submit" :disabled="loading"
              class="rounded-md bg-black px-4 py-2 text-white disabled:opacity-60">
        <span v-if="!loading">Inscribirme</span>
        <span v-else>Enviando…</span>
      </button>
    </form>

    <footer class="text-xs text-gray-500">
      * Al enviar, se validará duplicidad por email y recibirás un correo de verificación.
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useApi } from '../composables/useApi' // puedes dejar ../composables/useApi si prefieres

const api = useApi()

const form = reactive({ full_name: '', email: '', phone: '' })
const loading = ref(false)
const submitted = ref(false)
const successMsg = ref<string | null>(null)
const errorMsg = ref<string | null>(null)

const isEmailValid = computed(() => {
  const v = form.email.trim()
  return !!v && /\S+@\S+\.\S+/.test(v)
})

async function onSubmit() {
  submitted.value = true
  successMsg.value = null
  errorMsg.value = null

  if (!form.full_name || !isEmailValid.value || !form.phone) return

  loading.value = true
  try {
    const res = await api('/participants/register/', {
      method: 'POST',
      body: { full_name: form.full_name, email: form.email, phone: form.phone }
    }) as { message?: string; async?: boolean; task_id?: string }

    // Mensaje EXACTO del enunciado
    successMsg.value = res?.message ?? '¡Gracias por registrarte! Revisa tu correo para verificar tu cuenta.'
  } catch (err: any) {
    const status = err?.status || err?.response?.status
    if (status === 400) errorMsg.value = 'Este email ya está registrado'
    else errorMsg.value = err?.data?.detail || err?.data?.message || 'Ocurrió un error. Intenta nuevamente.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* mínimos estilos si no usas Tailwind aún */
input { outline: none; }
.text-gray-500 { color: #6b7280; }
.bg-black { background: #000; }
.text-white { color: #fff; }
.rounded-md { border-radius: 0.375rem; }
.border { border: 1px solid #e5e7eb; }
.p-2 { padding: 0.5rem; }
.p-3 { padding: 0.75rem; }
.p-6 { padding: 1.5rem; }
.mx-auto { margin-left: auto; margin-right: auto; }
.max-w-xl { max-width: 36rem; }
.space-y-4 > * + * { margin-top: 1rem; }
.space-y-6 > * + * { margin-top: 1.5rem; }
</style>
