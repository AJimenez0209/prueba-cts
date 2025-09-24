<template>
  <div class="mx-auto max-w-6xl p-6 space-y-8">
    <!-- Sección Registro (siempre visible) -->
    <section class="max-w-xl space-y-4">
      <header>
        <h1 class="text-2xl font-semibold">Inscripción al sorteo</h1>
        <p class="text-sm text-gray-500">Completa tus datos para participar.</p>
      </header>

      <div v-if="successMsg" class="rounded-md border border-green-300 bg-green-50 p-3 text-green-800">
        {{ successMsg }}
      </div>
      <div v-if="errorMsg" class="rounded-md border border-red-300 bg-red-50 p-3 text-red-800">
        {{ errorMsg }}
      </div>

      <div v-if="successMsg" class="mt-6 space-y-3 rounded-xl border p-4 bg-white">
        <h3 class="font-semibold">Verifica tu cuenta</h3>
        <p class="text-sm text-gray-600">
          Te enviamos un correo con un enlace. Si ya tienes el <strong>token</strong>, pégalo aquí y te llevamos a
          verificar.
        </p>

        <div class="flex flex-col sm:flex-row gap-2">
          <input v-model.trim="manualToken" type="text" placeholder="Pega tu token aquí"
            class="flex-1 rounded-lg border px-3 py-2 focus:ring-2 focus:ring-gray-300 outline-none" />
          <button @click="goVerifyWithToken()" :disabled="!manualToken"
            class="rounded-lg bg-gray-900 text-white px-4 py-2 disabled:opacity-60">
            Verificar ahora
          </button>
        </div>

        <!-- Botón DEV opcional: intenta obtener token automáticamente y redirige -->
        <div v-if="devAutoTokenEnabled" class="pt-1">
          <button @click="tryAutoFetchToken()" :disabled="autoLoading" class="rounded-lg border px-3 py-2">
            <span v-if="!autoLoading">Obtener token y verificar (dev)</span>
            <span v-else>Buscando token…</span>
          </button>
          <p v-if="autoError" class="text-xs text-red-600 mt-1">{{ autoError }}</p>
        </div>

        <p class="text-xs text-gray-500">
          * También puedes abrir el enlace desde tu correo para continuar el proceso.
        </p>
      </div>


      <form @submit.prevent="onSubmit" class="space-y-4">
        <div>
          <label class="block text-sm font-medium mb-1">Nombre completo</label>
          <input v-model.trim="form.full_name" type="text" class="w-full rounded-md border p-2"
            :class="{ 'border-red-400': submitted && !form.full_name }" placeholder="Ana Pérez" />
          <p v-if="submitted && !form.full_name" class="text-xs text-red-600 mt-1">Este campo es requerido.</p>
        </div>

        <div>
          <label class="block text-sm font-medium mb-1">Email</label>
          <input v-model.trim="form.email" type="email" class="w-full rounded-md border p-2"
            :class="{ 'border-red-400': submitted && !isEmailValid }" placeholder="ana@example.com" />
          <p v-if="submitted && !isEmailValid" class="text-xs text-red-600 mt-1">Ingresa un email válido.</p>
        </div>

        <div>
          <label class="block text-sm font-medium mb-1">Teléfono</label>
          <input v-model.trim="form.phone" type="text" class="w-full rounded-md border p-2"
            placeholder="+56 9 1234 5678" />
          <p v-if="submitted && !form.phone" class="text-xs text-red-600 mt-1">Este campo es requerido.</p>
        </div>

        <button type="submit" :disabled="loading" class="rounded-md bg-black px-4 py-2 text-white disabled:opacity-60">
          <span v-if="!loading">Inscribirme</span>
          <span v-else>Enviando…</span>
        </button>
      </form>

      <p class="text-xs text-gray-500">* Recibirás un correo para verificar tu cuenta.</p>
    </section>

    <!-- Sección Admin (cambia según sesión) -->
    <section>
      <header class="flex items-center gap-2">
        <h2 class="text-xl font-semibold">Panel Admin</h2>
        <span v-if="!admin.hasKey" class="text-sm text-gray-500"> (requiere API Key)</span>
      </header>

      <div v-if="!admin.hasKey" class="mt-3">
        <NuxtLink to="/admin/login" class="rounded-md bg-black px-3 py-2 text-white">Iniciar sesión</NuxtLink>
      </div>

      <div v-else class="mt-4 space-y-3">
        <div class="flex items-center justify-between">
          <div class="text-sm text-gray-600">Mostrando todos los participantes (verificados y no verificados)</div>
          <div class="flex items-center gap-2">
            <NuxtLink to="/admin/participants" class="rounded-md border px-3 py-2">Ver lista completa</NuxtLink>
            <NuxtLink to="/admin/draw" class="rounded-md bg-black px-3 py-2 text-white">Sortear ganador</NuxtLink>
          </div>
        </div>

        <!-- Tabla compacta -->
        <div v-if="adminLoading" class="rounded-md border p-3">Cargando…</div>
        <div v-else-if="adminError" class="rounded-md border border-red-300 bg-red-50 p-3 text-red-800">{{ adminError }}
        </div>
        <div v-else>
          <table class="w-full border-collapse">
            <thead>
              <tr class="text-left border-b">
                <th class="py-2 pr-3">Nombre</th>
                <th class="py-2 pr-3">Email</th>
                <th class="py-2 pr-3">Teléfono</th>
                <th class="py-2 pr-3">Verificado</th>
                <th class="py-2 pr-3">Fecha</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="p in previewRows" :key="p.id" class="border-b">
                <td class="py-2 pr-3">{{ p.full_name }}</td>
                <td class="py-2 pr-3">{{ p.email }}</td>
                <td class="py-2 pr-3">{{ p.phone }}</td>
                <td class="py-2 pr-3">{{ p.is_verified ? 'Sí' : 'No' }}</td>
                <td class="py-2 pr-3">{{ formatDate(p.created_at) }}</td>
              </tr>
            </tbody>
          </table>
          <div v-if="rows.length === 0" class="rounded-md border p-3 mt-2">Sin participantes aún.</div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useAdminStore } from '~/stores/admin'
import { useApi } from '~/composables/useApi'
// NUEVO: estado para verificación desde home
const manualToken = ref('')
const autoLoading = ref(false)
const autoError = ref<string | null>(null)

// Habilitar botón DEV solo si tienes un endpoint de debug en backend
// p.ej., algo como: GET /api/debug/last-token/?email=<email>
// Si no existe, deja en false y el botón no se muestra.
const devAutoTokenEnabled = false // 👈 pon true si implementas un endpoint de token

function goVerifyWithToken() {
  if (!manualToken.value) return
  navigateTo(`/verify?token=${encodeURIComponent(manualToken.value)}`)
}

async function tryAutoFetchToken() {
  autoError.value = null
  if (!form.email) {
    autoError.value = 'Ingresa tu email y regístrate para poder buscar el token.'
    return
  }
  autoLoading.value = true
  try {
    // EJEMPLO (ajusta a tu endpoint real si lo implementas):
    // const res = await api('/debug/last-token/', { method: 'GET', query: { email: form.email } }) as any
    // const token = String(res?.token || '')
    // if (!token) throw new Error('No se encontró token para ese email.')
    // navigateTo(`/verify?token=${encodeURIComponent(token)}`)

    // Sin endpoint → mostramos guía
    throw new Error('No hay endpoint de token habilitado. Revisa el correo o pega el token manualmente.')
  } catch (e: any) {
    autoError.value = e?.message || 'No se pudo obtener el token.'
  } finally {
    autoLoading.value = false
  }
}


const admin = useAdminStore()
const api = useApi()

// ----- Registro (público)
const form = reactive({ full_name: '', email: '', phone: '' })
const loading = ref(false)
const submitted = ref(false)
const successMsg = ref<string | null>(null)
const errorMsg = ref<string | null>(null)
const isEmailValid = computed(() => !!form.email.trim() && /\S+@\S+\.\S+/.test(form.email))

async function onSubmit() {
  submitted.value = true
  successMsg.value = null
  errorMsg.value = null
  if (!form.full_name || !isEmailValid.value || !form.phone) return

  loading.value = true
  try {
    const res = await api('/participants/register/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: { full_name: form.full_name, email: form.email, phone: form.phone }
    }) as { message?: string }
    successMsg.value = res?.message ?? '¡Gracias por registrarte! Revisa tu correo para verificar tu cuenta.'
    form.full_name = form.email = form.phone = ''
    submitted.value = false
  } catch (err: any) {
    const status = err?.status || err?.response?.status
    if (status === 400) errorMsg.value = 'Este email ya está registrado'
    else errorMsg.value = err?.data?.detail || err?.data?.message || 'Ocurrió un error. Intenta nuevamente.'
  } finally { loading.value = false }
}

// ----- Panel admin compacto (si logueado): lista TODOS
const adminLoading = ref(false)
const adminError = ref<string | null>(null)
const rows = ref<any[]>([])
const previewRows = computed(() => rows.value.slice(0, 5)) // muestra 5 en home

async function fetchAllParticipants() {
  if (!admin.hasKey) return
  adminLoading.value = true
  adminError.value = null
  try {
    const data = await api('/admin/participants/', {
      method: 'GET',
      query: { page: 1, page_size: 5 } // sin verified → trae todos
    }) as any
    rows.value = data?.results || []
  } catch (err: any) {
    const status = err?.status || err?.response?.status
    if (status === 401) { adminError.value = 'Sesión expirada. Inicia sesión nuevamente.'; admin.clear() }
    else adminError.value = err?.data?.detail || 'Error al cargar participantes.'
  } finally { adminLoading.value = false }
}

onMounted(fetchAllParticipants)
watch(() => admin.hasKey, (v) => { if (v) fetchAllParticipants() })

function formatDate(iso: string) { try { return new Date(iso).toLocaleString() } catch { return iso } }
</script>

<style scoped>
.text-gray-500 {
  color: #6b7280
}

.rounded-md {
  border-radius: 0.375rem
}

.border {
  border: 1px solid #e5e7eb
}

.p-2 {
  padding: 0.5rem
}

.p-3 {
  padding: 0.75rem
}

.p-6 {
  padding: 1.5rem
}

.mx-auto {
  margin: 0 auto
}

.max-w-6xl {
  max-width: 72rem
}

.max-w-xl {
  max-width: 36rem
}

.space-y-4>*+* {
  margin-top: 1rem
}

.space-y-8>*+* {
  margin-top: 2rem
}

.bg-black {
  background: #000
}

.text-white {
  color: #fff
}
</style>
