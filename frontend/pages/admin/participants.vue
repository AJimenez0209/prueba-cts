<template>
  <div class="mx-auto max-w-5xl p-6 space-y-6">
    <header class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-semibold">Participantes</h1>
        <p class="text-sm text-gray-500">Listado de concursantes verificados.</p>
      </div>

      <form @submit.prevent="applySearch" class="flex items-center gap-2">
        <input v-model.trim="search" type="text" placeholder="Buscar por nombre o email"
               class="rounded-md border p-2 w-64" />
        <button class="rounded-md bg-black px-3 py-2 text-white">Buscar</button>
      </form>
    </header>

    <div v-if="errorMsg" class="rounded-md border border-red-300 bg-red-50 p-3 text-red-800">
      {{ errorMsg }}
    </div>

    <div v-if="loading" class="rounded-md border p-3">Cargando…</div>

    <div v-if="!loading && rows.length === 0" class="rounded-md border p-3">
      Sin resultados.
    </div>

    <div v-if="rows.length">
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
          <tr v-for="p in rows" :key="p.id" class="border-b">
            <td class="py-2 pr-3">{{ p.full_name }}</td>
            <td class="py-2 pr-3">{{ p.email }}</td>
            <td class="py-2 pr-3">{{ p.phone }}</td>
            <td class="py-2 pr-3">{{ p.is_verified ? 'Sí' : 'No' }}</td>
            <td class="py-2 pr-3">{{ formatDate(p.created_at) }}</td>
          </tr>
        </tbody>
      </table>

      <div class="flex items-center justify-between mt-4">
        <button class="rounded-md border px-3 py-1" :disabled="page<=1" @click="goPrev">Anterior</button>
        <span>Página {{ page }} de {{ totalPages }}</span>
        <button class="rounded-md border px-3 py-1" :disabled="page>=totalPages" @click="goNext">Siguiente</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: ['require-admin'] })

import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApi } from '~/composables/useApi'

const api = useApi()
const route = useRoute()
const router = useRouter()

const loading = ref(false)
const errorMsg = ref<string | null>(null)

const page = ref<number>(Number(route.query.page || 1))
const pageSize = ref<number>(Number(route.query.page_size || 20))
const search = ref<string>(String(route.query.search || ''))

const rows = ref<any[]>([])
const totalPages = ref(1)

function syncQuery() {
  router.replace({
    query: {
      page: String(page.value),
      page_size: String(pageSize.value),
      ...(search.value ? { search: search.value } : {})
    }
  })
}

async function fetchList() {
  loading.value = true
  errorMsg.value = null
  try {
    const data = await api('/admin/participants/', {
      method: 'GET',
      query: {
        verified: 1,
        page: page.value,
        page_size: pageSize.value,
        ...(search.value ? { search: search.value } : {})
      }
    }) as any

    rows.value = data?.results || []
    totalPages.value = Number(data?.total_pages || 1)
  } catch (err: any) {
    const status = err?.status || err?.response?.status
    if (status === 401) {
      // si la API responde 401 → te mandamos a login
      return router.push('/admin/login')
    }
    errorMsg.value = err?.data?.detail || 'Error al cargar participantes.'
  } finally {
    loading.value = false
  }
}

function goPrev() { if (page.value > 1) { page.value--; syncQuery(); fetchList() } }
function goNext() { if (page.value < totalPages.value) { page.value++; syncQuery(); fetchList() } }
function applySearch() { page.value = 1; syncQuery(); fetchList() }

function formatDate(iso: string) {
  try { return new Date(iso).toLocaleString() } catch { return iso }
}

onMounted(fetchList)

// si cambian los query params desde el navegador
watch(() => route.query, () => {
  page.value = Number(route.query.page || 1)
  pageSize.value = Number(route.query.page_size || 20)
  search.value = String(route.query.search || '')
})
</script>

<style scoped>
.text-gray-500 { color: #6b7280; }
.rounded-md { border-radius: 0.375rem; }
.border { border: 1px solid #e5e7eb; }
.p-2 { padding: 0.5rem; }
.p-6 { padding: 1.5rem; }
.max-w-5xl { max-width: 64rem; }
.mx-auto { margin-left: auto; margin-right: auto; }
</style>
