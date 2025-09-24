<template>
  <nav class="sticky top-0 z-40 bg-white/80 backdrop-blur border-b border-gray-200">
    <div class="container max-w-6xl h-14 flex items-center">
      <NuxtLink to="/" class="font-semibold tracking-tight">Sorteo San Valentín</NuxtLink>

      <div class="ml-auto hidden sm:flex items-center gap-2">
        <template v-if="admin.hasKey">
          <NuxtLink to="/admin/participants" class="px-3 py-1.5 rounded-lg hover:bg-gray-100">Participantes</NuxtLink>
          <NuxtLink to="/admin/draw" class="px-3 py-1.5 rounded-lg hover:bg-gray-100">Sortear</NuxtLink>
          <button class="px-3 py-1.5 rounded-lg bg-gray-900 text-white" @click="logout">Salir</button>
        </template>
        <template v-else>
          <NuxtLink to="/admin/login" class="px-3 py-1.5 rounded-lg bg-gray-900 text-white">Login</NuxtLink>
        </template>
      </div>

      <!-- móvil -->
      <details class="sm:hidden ml-auto">
        <summary class="px-3 py-1.5 rounded-lg border">Menú</summary>
        <div class="absolute right-3 mt-2 w-44 app-card p-2 flex flex-col gap-1 bg-white">
          <template v-if="admin.hasKey">
            <NuxtLink to="/admin/participants" class="px-2 py-1 rounded hover:bg-gray-100">Participantes</NuxtLink>
            <NuxtLink to="/admin/draw" class="px-2 py-1 rounded hover:bg-gray-100">Sortear</NuxtLink>
            <button class="px-2 py-1 rounded hover:bg-gray-100 text-left" @click="logout">Salir</button>
          </template>
          <template v-else>
            <NuxtLink to="/admin/login" class="px-2 py-1 rounded hover:bg-gray-100">Login</NuxtLink>
          </template>
        </div>
      </details>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { useAdminStore } from '~/stores/admin'
const admin = useAdminStore()
function logout(){ admin.clear(); navigateTo('/admin/login') }
</script>
