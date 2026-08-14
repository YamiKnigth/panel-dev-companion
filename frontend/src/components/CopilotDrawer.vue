<template>
  <!-- Copilot Sidebar Drawer -->
  <div
    class="fixed top-0 right-0 h-full w-80 bg-slate-900 border-l border-slate-800 shadow-2xl z-40 transition-transform duration-300 flex flex-col justify-between"
    :class="isOpen ? 'translate-x-0' : 'translate-x-full'"
  >
    <!-- Drawer Header -->
    <div class="p-4 border-b border-slate-800 flex items-center justify-between">
      <div class="flex items-center gap-2">
        <span class="text-lg">🤖</span>
        <div>
          <h3 class="font-bold text-white text-sm">Copilot / Caddy IA</h3>
          <p class="text-[10px] text-emerald-400">Agente Experto en Minecraft</p>
        </div>
      </div>
      <button @click="$emit('close')" class="text-slate-400 hover:text-white p-1">✕</button>
    </div>

    <!-- Chat Messages History -->
    <div ref="chatContainer" class="flex-1 p-4 overflow-y-auto space-y-3 text-xs">
      <div v-if="messages.length === 0" class="text-center text-slate-500 py-8">
        ¡Hola! Soy tu Copilot de Minecraft. Hazme cualquier pregunta sobre tu servidor, plugins, errores o archivos.
      </div>

      <div
        v-for="(msg, idx) in messages"
        :key="idx"
        class="flex flex-col space-y-1"
        :class="msg.role === 'user' ? 'items-end' : 'items-start'"
      >
        <span class="text-[9px] text-slate-500 px-1">{{ msg.role === 'user' ? 'Tú' : 'Copilot IA' }}</span>
        <div
          class="p-3 rounded-xl max-w-[85%] leading-relaxed whitespace-pre-wrap"
          :class="msg.role === 'user' ? 'bg-emerald-600 text-white rounded-br-none' : 'bg-slate-950 border border-slate-800 text-slate-200 rounded-bl-none'"
        >
          {{ msg.content }}
        </div>
      </div>
    </div>

    <!-- Drawer Input Footer -->
    <div class="p-4 border-t border-slate-800 space-y-2 bg-slate-950">
      <div class="flex gap-2">
        <input
          v-model="userMsg"
          @keyup.enter="sendMessage"
          type="text"
          placeholder="Pregunta a la IA..."
          class="flex-1 bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-100 placeholder-slate-600 focus:outline-none focus:border-indigo-500"
        />
        <button
          @click="sendMessage"
          :disabled="sending || !userMsg.trim()"
          class="bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 text-white text-xs px-3 py-2 rounded-lg cursor-pointer font-semibold"
        >
          Enviar
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, nextTick } from 'vue'
import axios from 'axios'

const props = defineProps({
  isOpen: Boolean,
  server: Object,
  jwtToken: String
})

defineEmits(['close'])

const messages = ref([])
const userMsg = ref('')
const sending = ref(false)
const chatContainer = ref(null)

const scrollToBottom = async () => {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

const fetchHistory = async () => {
  if (!props.server?.identifier) return
  try {
    const res = await axios.get(`/api/servers/${props.server.identifier}/ai/chat`, {
      headers: { Authorization: `Bearer ${props.jwtToken}` }
    })
    messages.value = res.data.history || []
    scrollToBottom()
  } catch (err) {
    console.error('Error cargando historial del chat:', err)
  }
}

const sendMessage = async () => {
  const text = userMsg.value.trim()
  if (!text || !props.server?.identifier) return

  messages.value.push({ role: 'user', content: text })
  userMsg.value = ''
  sending.value = true
  scrollToBottom()

  try {
    const res = await axios.post(`/api/servers/${props.server.identifier}/ai/chat`, {
      message: text
    }, {
      headers: { Authorization: `Bearer ${props.jwtToken}` }
    })

    messages.value.push({ role: 'model', content: res.data.reply })
    scrollToBottom()
  } catch (err) {
    messages.value.push({ role: 'model', content: `Error: ${err.response?.data?.detail || 'Fallo de conexión con Copilot'}` })
    scrollToBottom()
  } finally {
    sending.value = false
  }
}

watch(() => props.server, () => {
  fetchHistory()
}, { immediate: true })
</script>
