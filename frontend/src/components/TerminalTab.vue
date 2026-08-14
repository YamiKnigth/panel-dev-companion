<template>
  <div class="space-y-4">
    <div class="bg-slate-950 border border-slate-800 rounded-xl p-4 font-mono text-sm h-[480px] overflow-y-auto flex flex-col justify-between">
      <div class="space-y-2 whitespace-pre-wrap text-slate-300">
        <div v-for="(log, idx) in logs" :key="idx" class="leading-relaxed">
          {{ log }}
        </div>
        <div v-if="logs.length === 0" class="text-slate-600 italic">
          No hay salidas en la consola aún. Escribe un comando abajo para interactuar.
        </div>
      </div>
    </div>

    <div class="flex items-center gap-3">
      <div class="flex-1 flex bg-slate-900 border border-slate-800 rounded-xl p-1 focus-within:border-emerald-500 transition-colors">
        <span class="px-3 py-2 text-slate-500 font-mono text-sm">$</span>
        <input
          v-model="command"
          @keyup.enter="sendCommand"
          type="text"
          placeholder="Escribe un comando de consola (ej. say Hola, op player, help)..."
          class="w-full bg-transparent border-none text-slate-100 placeholder-slate-600 focus:outline-none text-sm font-mono py-2 pr-3"
        />
      </div>
      <button
        @click="sendCommand"
        :disabled="sending"
        class="bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-800 text-white font-medium px-5 py-2.5 rounded-xl text-sm transition-colors cursor-pointer flex items-center gap-2"
      >
        <span>Enviar</span>
      </button>

      <button
        @click="analyzeLogs"
        :disabled="analyzing || logs.length === 0"
        class="bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 text-white font-medium px-4 py-2.5 rounded-xl text-sm transition-colors cursor-pointer flex items-center gap-2"
      >
        <span>🔍 Analizar Error con IA</span>
      </button>
    </div>

    <!-- AI Analysis Result Modal / Alert -->
    <div v-if="aiAnalysis" class="bg-indigo-950/40 border border-indigo-500/30 rounded-xl p-5 text-indigo-200 text-sm space-y-2 relative">
      <button @click="aiAnalysis = ''" class="absolute top-3 right-3 text-indigo-400 hover:text-white">✕</button>
      <h4 class="font-bold text-indigo-300 flex items-center gap-2">
        <span>✨ Análisis de Diagnóstico IA</span>
      </h4>
      <div class="whitespace-pre-wrap font-sans leading-relaxed text-indigo-100">
        {{ aiAnalysis }}
      </div>
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

const command = ref('')
const sending = ref(false)
const analyzing = ref(false)
const logs = ref([])
const aiAnalysis = ref('')

const sendCommand = async () => {
  const cmd = command.value.trim()
  if (!cmd) return

  sending.value = true
  logs.value.push(`> ${cmd}`)
  command.value = ''

  try {
    await axios.post(`/api/servers/${props.server.identifier}/command`, { command: cmd }, {
      headers: { Authorization: `Bearer ${props.jwtToken}` }
    })
    logs.value.push(`[PteroDev] Comando enviado con éxito (204 No Content)`)
  } catch (err) {
    logs.value.push(`[Error] ${err.response?.data?.detail || 'No se pudo enviar el comando'}`)
  } finally {
    sending.value = false
  }
}

const analyzeLogs = async () => {
  analyzing.value = true
  aiAnalysis.value = ''

  const logsText = logs.value.slice(-50).join('\n')
  try {
    const res = await axios.post(`/api/servers/${props.server.identifier}/ai/analyze-logs`, {
      logs: logsText
    }, {
      headers: { Authorization: `Bearer ${props.jwtToken}` }
    })
    aiAnalysis.value = res.data.analysis
  } catch (err) {
    aiAnalysis.value = `Error de análisis: ${err.response?.data?.detail || 'No se pudo conectar con el motor IA'}`
  } finally {
    analyzing.value = false
  }
}
</script>
