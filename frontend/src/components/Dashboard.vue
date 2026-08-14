<template>
  <div class="max-w-7xl mx-auto p-6 space-y-6">
    <div class="flex items-center justify-between border-b border-slate-800 pb-5">
      <div>
        <h2 class="text-xl font-bold text-white">Servidores de Desarrollo</h2>
        <p class="text-sm text-slate-400">Selecciona o desbloquea un servidor propio para comenzar</p>
      </div>
      <button @click="$emit('logout')" class="text-xs text-slate-400 hover:text-slate-200 px-3 py-2 bg-slate-900 border border-slate-800 rounded-lg">
        Cerrar Sesión
      </button>
    </div>

    <div v-if="servers.length === 0" class="text-center py-12 text-slate-500">
      No se encontraron servidores donde seas el propietario (`server_owner: true`).
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="srv in servers"
        :key="srv.attributes.identifier"
        class="bg-slate-900 border border-slate-800 rounded-xl p-5 flex flex-col justify-between hover:border-slate-700 transition-all"
      >
        <div>
          <div class="flex items-start justify-between gap-3 mb-3">
            <div>
              <h3 class="font-semibold text-white text-lg">{{ srv.attributes.name }}</h3>
              <p class="text-xs text-slate-500 font-mono">ID: {{ srv.attributes.identifier }} | Nodo: {{ srv.attributes.node }}</p>
            </div>
            <span
              class="px-2 py-1 text-xs rounded font-medium"
              :class="srv.attributes.is_unlocked ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-red-500/10 text-red-400 border border-red-500/20'"
            >
              {{ srv.attributes.is_unlocked ? 'Desbloqueado' : 'Bloqueado' }}
            </span>
          </div>
        </div>

        <div class="mt-6 border-t border-slate-800/80 pt-4">
          <!-- Unlocked State -->
          <div v-if="srv.attributes.is_unlocked">
            <button
              @click="$emit('select-server', srv.attributes)"
              class="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-medium py-2.5 rounded-lg text-sm transition-colors cursor-pointer flex items-center justify-center gap-2"
            >
              <span>Entrar al Servidor</span>
              <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
            </button>
          </div>

          <!-- Locked State -->
          <div v-else class="space-y-3">
            <div class="flex items-center gap-2 text-xs text-slate-400">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
              <span>Ingresa el API Key del Servidor para desbloquear:</span>
            </div>

            <div class="flex gap-2">
              <input
                v-model="tokens[srv.attributes.identifier]"
                type="password"
                placeholder="ptlc_token_servidor"
                class="flex-1 bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-emerald-500"
              />
              <button
                @click="unlockServer(srv.attributes.identifier)"
                :disabled="unlocking[srv.attributes.identifier]"
                class="bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium px-3 py-2 rounded-lg transition-colors cursor-pointer"
              >
                {{ unlocking[srv.attributes.identifier] ? '...' : 'Desbloquear' }}
              </button>
            </div>
            <p v-if="unlockError[srv.attributes.identifier]" class="text-xs text-red-400">
              {{ unlockError[srv.attributes.identifier] }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import axios from 'axios'

const props = defineProps({
  servers: Array,
  jwtToken: String
})

const emit = defineEmits(['select-server', 'refresh-servers', 'logout'])

const tokens = reactive({})
const unlocking = reactive({})
const unlockError = reactive({})

const unlockServer = async (identifier) => {
  const token = tokens[identifier]?.trim()
  if (!token) return

  unlocking[identifier] = true
  unlockError[identifier] = ''

  try {
    await axios.post('/api/servers/unlock', {
      identifier,
      token
    }, {
      headers: { Authorization: `Bearer ${props.jwtToken}` }
    })

    emit('refresh-servers')
  } catch (err) {
    unlockError[identifier] = err.response?.data?.detail || 'Token inválido para este servidor'
  } finally {
    unlocking[identifier] = false
  }
}
</script>
