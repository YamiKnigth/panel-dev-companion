<template>
  <div class="max-w-2xl mx-auto bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-6">
    <div>
      <h3 class="text-lg font-bold text-white">Sincronización de Repositorio Git</h3>
      <p class="text-xs text-slate-400">Clona un repositorio remoto e inyecta los archivos en tu servidor de Pterodactyl</p>
    </div>

    <form @submit.prevent="handleGitSync" class="space-y-4">
      <div>
        <label class="block text-xs font-medium text-slate-300 mb-2">URL del Repositorio Git</label>
        <input
          v-model="repoUrl"
          type="url"
          placeholder="https://github.com/usuario/mi-plugin-minecraft.git"
          required
          class="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-2.5 text-xs text-slate-100 placeholder-slate-600 focus:outline-none focus:border-emerald-500"
        />
      </div>

      <div>
        <label class="block text-xs font-medium text-slate-300 mb-2">Rama (Branch)</label>
        <input
          v-model="branch"
          type="text"
          placeholder="main"
          class="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-2.5 text-xs text-slate-100 placeholder-slate-600 focus:outline-none focus:border-emerald-500"
        />
      </div>

      <button
        type="submit"
        :disabled="syncing"
        class="w-full bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-800 text-white font-semibold py-3 px-4 rounded-lg text-xs transition-colors cursor-pointer flex items-center justify-center gap-2"
      >
        <span>{{ syncing ? 'Sincronizando Archivos...' : '🚀 Hacer Deploy / Sincronizar' }}</span>
      </button>
    </form>

    <div v-if="result" class="bg-slate-950 border border-slate-800 rounded-xl p-4 text-xs space-y-2">
      <div class="font-bold text-emerald-400">{{ result.message }}</div>
      <p class="text-slate-400">Archivos sincronizados con éxito: <span class="font-bold text-white">{{ result.total_synced }}</span></p>
      <ul v-if="result.synced_files.length" class="max-h-32 overflow-y-auto space-y-1 font-mono text-[11px] text-slate-300">
        <li v-for="sf in result.synced_files" :key="sf">✓ {{ sf }}</li>
      </ul>
    </div>

    <div v-if="error" class="bg-red-500/10 border border-red-500/20 text-red-400 rounded-xl p-4 text-xs">
      {{ error }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const props = defineProps({
  server: Object,
  jwtToken: String
})

const repoUrl = ref('')
const branch = ref('main')
const syncing = ref(false)
const result = ref(null)
const error = ref('')

const handleGitSync = async () => {
  if (!repoUrl.value.trim()) return
  syncing.value = true
  result.value = null
  error.value = ''

  try {
    const res = await axios.post(`/api/servers/${props.server.identifier}/git/sync`, {
      repo_url: repoUrl.value.trim(),
      branch: branch.value.trim() || 'main'
    }, {
      headers: { Authorization: `Bearer ${props.jwtToken}` }
    })
    result.value = res.data
  } catch (err) {
    error.value = err.response?.data?.detail || 'Error en la sincronización Git'
  } finally {
    syncing.value = false
  }
}
</script>
