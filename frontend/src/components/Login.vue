<template>
  <div class="min-h-screen flex items-center justify-center bg-slate-950 p-4">
    <div class="max-w-md w-full bg-slate-900 border border-slate-800 rounded-xl p-8 shadow-2xl">
      <div class="flex items-center justify-center gap-3 mb-6">
        <div class="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-lg text-emerald-400">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M12 5l7 7-7 7" />
          </svg>
        </div>
        <div>
          <h1 class="text-2xl font-bold text-white tracking-tight">PteroDev Companion</h1>
          <p class="text-xs text-slate-400">Entorno Aislado & Copiloto para Pterodactyl</p>
        </div>
      </div>

      <form @submit.prevent="handleLogin" class="space-y-5">
        <div>
          <label class="block text-sm font-medium text-slate-300 mb-2">Master API Key (Pterodactyl)</label>
          <input
            v-model="apiKey"
            type="password"
            placeholder="ptlc_xxxxxxxxxxxxxxxx"
            required
            class="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-3 text-slate-100 placeholder-slate-600 focus:outline-none focus:border-emerald-500 transition-colors"
          />
        </div>

        <div v-if="error" class="p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm">
          {{ error }}
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-800 text-white font-semibold py-3 px-4 rounded-lg transition-colors flex items-center justify-center gap-2 cursor-pointer"
        >
          <span v-if="loading" class="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></span>
          <span>{{ loading ? 'Conectando...' : 'Iniciar Sesión' }}</span>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const emit = defineEmits(['login-success'])
const apiKey = ref('')
const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  try {
    const res = await axios.post('/api/auth/login', { api_key: apiKey.value })
    emit('login-success', {
      token: res.data.token,
      servers: res.data.servers
    })
  } catch (err) {
    error.value = err.response?.data?.detail || 'Error de autenticación con el servidor'
  } finally {
    loading.value = false
  }
}
</script>
