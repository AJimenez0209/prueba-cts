<template>
  <div class="mx-auto max-w-xl p-6 space-y-6">
    <header class="space-y-1">
      <h1 class="text-2xl font-semibold">Verificación de correo</h1>
      <p class="text-sm text-gray-500">Validaremos tu token y podrás crear tu contraseña.</p>
    </header>

    <!-- Estados de verificación -->
    <div v-if="verify.loading" class="rounded-md border p-3">Verificando token…</div>
    <div v-if="verify.error" class="rounded-md border border-red-300 bg-red-50 p-3 text-red-800">
      {{ verify.error }}
    </div>
    <div v-if="verify.success && !password.done" class="rounded-md border border-green-300 bg-green-50 p-3 text-green-800">
      Correo verificado correctamente. Crea tu contraseña para activar la cuenta.
    </div>

    <!-- Form set password -->
    <form v-if="verify.success && !password.done" @submit.prevent="onSetPassword" class="space-y-4">
      <div>
        <label class="block text-sm font-medium mb-1">Nueva contraseña</label>
        <input v-model.trim="password.value" type="password" class="w-full rounded-md border p-2"
               :class="{'border-red-400': password.submitted && !isPassValid}" placeholder="********" />
        <p v-if="password.submitted && !isPassValid" class="text-xs text-red-600 mt-1">
          Mínimo 8 caracteres.
        </p>
      </div>

      <button type="submit" :disabled="password.loading"
              class="rounded-md bg-black px-4 py-2 text-white disabled:opacity-60">
        <span v-if="!password.loading">Guardar contraseña</span>
        <span v-else>Guardando…</span>
      </button>
    </form>

    <!-- Mensaje final requerido -->
    <div v-if="password.done" class="rounded-md border border-green-300 bg-green-50 p-3 text-green-800">
      Tu cuenta ha sido activada. Ya estás participando en el sorteo.
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useApi } from '~/composables/useApi'

const api = useApi()
const route = useRoute()

// estado verificación
const verify = reactive({
  loading: true,
  success: false,
  error: '' as string,
  participantId: null as number | null
})

// estado password
const password = reactive({
  value: '',
  loading: false,
  submitted: false,
  done: false
})

const isPassValid = computed(() => password.value.length >= 8)

onMounted(async () => {
  // token desde ?token=... (o soporta #token=... si quieres)
  const token = String(route.query.token || '').trim()
  if (!token) {
    verify.loading = false
    verify.error = 'Token de verificación no encontrado.'
    return
  }

  try {
    const res = await api(`/participants/verify/${encodeURIComponent(token)}/`, { method: 'GET' }) as any
    verify.participantId = Number(res?.participant_id ?? res?.participantId ?? null)
    verify.success = true
  } catch (err: any) {
    verify.error = err?.data?.detail || 'Token inválido o expirado.'
  } finally {
    verify.loading = false
  }
})

async function onSetPassword() {
  password.submitted = true
  if (!isPassValid.value || !verify.participantId) return

  password.loading = true
  try {
    await api(`/participants/set-password/${verify.participantId}/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: { password: password.value }
    })
    // Mensaje final literal
    password.done = true
  } catch (err: any) {
    // feedback básico
    alert(err?.data?.detail || 'No se pudo guardar la contraseña. Intenta nuevamente.')
  } finally {
    password.loading = false
  }
}
</script>

<style scoped>
.text-gray-500 { color: #6b7280; }
.rounded-md { border-radius: 0.375rem; }
.border { border: 1px solid #e5e7eb; }
.p-2 { padding: 0.5rem; }
.p-3 { padding: 0.75rem; }
.p-6 { padding: 1.5rem; }
.mx-auto { margin-left: auto; margin-right: auto; }
.max-w-xl { max-width: 36rem; }
.space-y-4 > * + * { margin-top: 1rem; }
.space-y-6 > * + * { margin-top: 1.5rem; }
.bg-black { background: #000; }
.text-white { color: #fff; }
</style>
