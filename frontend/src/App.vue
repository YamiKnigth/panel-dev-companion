<template>
  <div class="min-h-screen bg-slate-950 text-slate-100 font-sans flex flex-col">
    <!-- Unauthenticated View -->
    <Login v-if="!sessionToken" @login-success="onLoginSuccess" />

    <!-- Authenticated View -->
    <template v-else>
      <!-- Navigation Header -->
      <header class="border-b border-slate-800 bg-slate-900/50 backdrop-blur sticky top-0 z-30">
        <div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="p-2 bg-emerald-500/10 border border-emerald-500/20 rounded-lg text-emerald-400 font-bold text-lg">
              PD
            </div>
            <div>
              <h1 class="font-bold text-white tracking-tight">PteroDev Companion</h1>
              <p v-if="selectedServer" class="text-xs text-slate-400 font-mono">
                Servidor Activo: <span class="text-emerald-400 font-semibold">{{ selectedServer.name }}</span> ({{ selectedServer.identifier }})
              </p>
            </div>
          </div>

          <div class="flex items-center gap-3">
            <button
              v-if="selectedServer"
              @click="isCopilotOpen = !isCopilotOpen"
              class="bg-indigo-600/20 hover:bg-indigo-600/30 border border-indigo-500/30 text-indigo-300 px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-2 cursor-pointer"
            >
              <span>🤖 Caddy / Copilot IA</span>
            </button>

            <button
              v-if="selectedServer"
              @click="selectedServer = null"
              class="bg-slate-800 hover:bg-slate-700 text-slate-200 px-3 py-1.5 rounded-lg text-xs font-medium cursor-pointer"
            >
              Volver al Dashboard
            </button>

            <button
              @click="logout"
              class="text-xs text-slate-400 hover:text-white px-3 py-1.5 border border-slate-800 rounded-lg hover:bg-slate-800 cursor-pointer"
            >
              Salir
            </button>
          </div>
        </div>
      </header>

      <!-- Main Dashboard or Server Management Tabs -->
      <main class="flex-1">
        <!-- Dashboard List -->
        <Dashboard
          v-if="!selectedServer"
          :servers="servers"
          :jwtToken="sessionToken"
          @select-server="onSelectServer"
          @refresh-servers="fetchServers"
          @logout="logout"
        />

        <!-- Active Server View -->
        <div v-else class="max-w-7xl mx-auto p-6 space-y-6">
          <!-- Tab Selection Header -->
          <div class="flex items-center gap-2 border-b border-slate-800 pb-3">
            <button
              @click="activeTab = 'terminal'"
              class="px-4 py-2 text-xs font-semibold rounded-lg transition-colors cursor-pointer"
              :class="activeTab === 'terminal' ? 'bg-emerald-600 text-white' : 'text-slate-400 hover:bg-slate-900'"
            >
              💻 Consola Terminal
            </button>
            <button
              @click="activeTab = 'editor'"
              class="px-4 py-2 text-xs font-semibold rounded-lg transition-colors cursor-pointer"
              :class="activeTab === 'editor' ? 'bg-emerald-600 text-white' : 'text-slate-400 hover:bg-slate-900'"
            >
              📝 Editor de Código
            </button>
            <button
              @click="activeTab = 'git'"
              class="px-4 py-2 text-xs font-semibold rounded-lg transition-colors cursor-pointer"
              :class="activeTab === 'git' ? 'bg-emerald-600 text-white' : 'text-slate-400 hover:bg-slate-900'"
            >
              🔄 Git Sync
            </button>
          </div>

          <!-- Tab Content Views -->
          <TerminalTab v-if="activeTab === 'terminal'" :server="selectedServer" :jwtToken="sessionToken" />
          <EditorTab v-if="activeTab === 'editor'" :server="selectedServer" :jwtToken="sessionToken" />
          <GitSyncTab v-if="activeTab === 'git'" :server="selectedServer" :jwtToken="sessionToken" />
        </div>
      </main>

      <!-- Copilot Drawer Component -->
      <CopilotDrawer
        :isOpen="isCopilotOpen"
        :server="selectedServer"
        :jwtToken="sessionToken"
        @close="isCopilotOpen = false"
      />
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Login from './components/Login.vue'
import Dashboard from './components/Dashboard.vue'
import TerminalTab from './components/TerminalTab.vue'
import EditorTab from './components/EditorTab.vue'
import GitSyncTab from './components/GitSyncTab.vue'
import CopilotDrawer from './components/CopilotDrawer.vue'

const sessionToken = ref(localStorage.getItem('companion_jwt') || '')
const servers = ref([])
const selectedServer = ref(null)
const activeTab = ref('terminal')
const isCopilotOpen = ref(false)

const onLoginSuccess = (data) => {
  sessionToken.value = data.token
  servers.value = data.servers
  localStorage.setItem('companion_jwt', data.token)
}

const fetchServers = async () => {
  // En caso de refresco, reutilizar el token si existe o requerir re-login
}

const onSelectServer = (srvAttrs) => {
  selectedServer.value = srvAttrs
  activeTab.value = 'terminal'
}

const logout = () => {
  sessionToken.value = ''
  servers.value = []
  selectedServer.value = null
  localStorage.removeItem('companion_jwt')
}
</script>
