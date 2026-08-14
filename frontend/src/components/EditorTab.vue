<template>
  <div class="grid grid-cols-1 md:grid-cols-4 gap-6 h-[600px]">
    <!-- File Browser Sidebar -->
    <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col justify-between overflow-y-auto">
      <div>
        <div class="flex items-center justify-between mb-4">
          <h3 class="font-semibold text-slate-200 text-sm">Archivos del Servidor</h3>
          <button @click="fetchFiles" class="text-xs text-slate-400 hover:text-white">🔄 Refrescar</button>
        </div>

        <div v-if="loadingFiles" class="text-xs text-slate-500 py-4 text-center">
          Cargando archivos...
        </div>

        <ul v-else class="space-y-1 text-xs">
          <li
            v-for="f in files"
            :key="f.attributes.name"
            @click="selectFile(f)"
            class="px-3 py-2 rounded-lg cursor-pointer flex items-center justify-between transition-colors"
            :class="selectedFilePath === f.attributes.name ? 'bg-emerald-500/10 text-emerald-400 font-medium' : 'text-slate-300 hover:bg-slate-800'"
          >
            <span class="truncate">{{ f.attributes.name }}</span>
            <span class="text-[10px] text-slate-500">{{ f.attributes.mode_bits }}</span>
          </li>
        </ul>
      </div>
    </div>

    <!-- Code Editor Area -->
    <div class="md:col-span-3 bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col justify-between space-y-4">
      <div class="flex items-center justify-between border-b border-slate-800 pb-3">
        <div class="flex items-center gap-2">
          <span class="text-xs text-slate-400">Archivo:</span>
          <span class="font-mono text-sm text-emerald-400 font-medium">{{ selectedFilePath || 'Ninguno seleccionado' }}</span>
        </div>

        <div class="flex items-center gap-3">
          <button
            v-if="selectedFilePath"
            @click="showAiPromptModal = true"
            class="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium px-3 py-1.5 rounded-lg transition-colors flex items-center gap-1.5 cursor-pointer"
          >
            <span>✨ Modificar con IA</span>
          </button>

          <button
            v-if="selectedFilePath"
            @click="saveFile"
            :disabled="saving"
            class="bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-800 text-white text-xs font-medium px-4 py-1.5 rounded-lg transition-colors flex items-center gap-1.5 cursor-pointer"
          >
            <span>{{ saving ? 'Guardando...' : '💾 Guardar' }}</span>
          </button>
        </div>
      </div>

      <!-- Editor Textarea -->
      <div class="flex-1 relative">
        <textarea
          v-model="fileContent"
          placeholder="Selecciona un archivo para editar su contenido..."
          class="w-full h-full bg-slate-950 border border-slate-800 rounded-xl p-4 font-mono text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-emerald-500 resize-none leading-relaxed"
        ></textarea>
      </div>

      <p v-if="statusMessage" class="text-xs" :class="statusIsError ? 'text-red-400' : 'text-emerald-400'">
        {{ statusMessage }}
      </p>
    </div>

    <!-- AI Prompt Modal -->
    <div v-if="showAiPromptModal" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div class="bg-slate-900 border border-slate-800 rounded-xl p-6 max-w-lg w-full space-y-4 shadow-2xl">
        <h3 class="text-lg font-bold text-white flex items-center gap-2">
          <span>✨ Modificar {{ selectedFilePath }} con IA</span>
        </h3>
        <p class="text-xs text-slate-400">Describe las modificaciones que deseas realizar en este archivo:</p>
        <textarea
          v-model="aiPromptInput"
          placeholder="Ej: Cambia el puerto a 25565, habilita PVP y optimiza la configuración..."
          class="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500 h-28"
        ></textarea>

        <div class="flex justify-end gap-3 pt-2">
          <button
            @click="showAiPromptModal = false"
            class="px-4 py-2 bg-slate-800 text-slate-300 text-xs rounded-lg hover:bg-slate-700"
          >
            Cancelar
          </button>
          <button
            @click="applyAiEdit"
            :disabled="applyingAi || !aiPromptInput.trim()"
            class="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg disabled:bg-slate-800 cursor-pointer"
          >
            {{ applyingAi ? 'Procesando e Inyectando...' : 'Aplicar Modificación' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const props = defineProps({
  server: Object,
  jwtToken: String
})

const files = ref([])
const loadingFiles = ref(false)
const selectedFilePath = ref('')
const fileContent = ref('')
const saving = ref(false)
const statusMessage = ref('')
const statusIsError = ref(false)

const showAiPromptModal = ref(false)
const aiPromptInput = ref('')
const applyingAi = ref(false)

const fetchFiles = async () => {
  loadingFiles.value = true
  try {
    const res = await axios.get(`/api/servers/${props.server.identifier}/files/list?directory=/`, {
      headers: { Authorization: `Bearer ${props.jwtToken}` }
    })
    files.value = res.data.data || []
  } catch (err) {
    statusMessage.value = 'Error al cargar lista de archivos'
    statusIsError.value = true
  } finally {
    loadingFiles.value = false
  }
}

const selectFile = async (f) => {
  selectedFilePath.value = f.attributes.name
  statusMessage.value = ''
  try {
    const res = await axios.get(`/api/servers/${props.server.identifier}/files/contents?file=/${f.attributes.name}`, {
      headers: { Authorization: `Bearer ${props.jwtToken}` }
    })
    fileContent.value = res.data
  } catch (err) {
    statusMessage.value = 'Error al leer contenido del archivo'
    statusIsError.value = true
  }
}

const saveFile = async () => {
  if (!selectedFilePath.value) return
  saving.value = true
  statusMessage.value = ''
  statusIsError.value = false

  try {
    await axios.post(`/api/servers/${props.server.identifier}/files/write?file=/${selectedFilePath.value}`, fileContent.value, {
      headers: {
        Authorization: `Bearer ${props.jwtToken}`,
        'Content-Type': 'text/plain'
      }
    })
    statusMessage.value = 'Archivo guardado correctamente'
  } catch (err) {
    statusMessage.value = 'Error al guardar archivo'
    statusIsError.value = true
  } finally {
    saving.value = false
  }
}

const applyAiEdit = async () => {
  if (!selectedFilePath.value || !aiPromptInput.value.trim()) return
  applyingAi.value = true

  try {
    const res = await axios.post(`/api/servers/${props.server.identifier}/ai/edit-file`, {
      file_path: `/${selectedFilePath.value}`,
      user_prompt: aiPromptInput.value.trim()
    }, {
      headers: { Authorization: `Bearer ${props.jwtToken}` }
    })

    fileContent.value = res.data.new_content
    statusMessage.value = 'Archivo modificado e inyectado con éxito por la IA'
    statusIsError.value = false
    showAiPromptModal.value = false
    aiPromptInput.value = ''
  } catch (err) {
    statusMessage.value = `Error IA: ${err.response?.data?.detail || 'Fallo al aplicar modificación'}`
    statusIsError.value = true
  } finally {
    applyingAi.value = false
  }
}

onMounted(() => {
  fetchFiles()
})
</script>
