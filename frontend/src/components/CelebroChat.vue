<script setup>
import { ref, onMounted, nextTick } from 'vue';
import api from '../services/api';

const messages = ref([
  { role: 'system', text: 'TERMINAL INICIALIZADO. ESTRATEGISTA DE TRÁFEGO FRIO ONLINE.' },
  { role: 'ai', text: 'Aguardando parâmetros para análise de ROAS e CPA. Como posso otimizar seu capital hoje?' }
]);

const newMessage = ref('');
const loading = ref(false);
const uploading = ref(false);
const chatContainer = ref(null);
const fileInput = ref(null);
const brainFileInput = ref(null);
const isUploadModalOpen = ref(false);
const selectedCategory = ref('BRANDING');

const scrollToBottom = async () => {
  await nextTick();
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
  }
};

const toggleUploadModal = () => {
  isUploadModalOpen.value = !isUploadModalOpen.value;
};

const handleBrainUpload = async (event) => {
  const file = event.target.files[0];
  if (!file) return;

  uploading.value = true;
  try {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('category', selectedCategory.value);

    await api.post('/brain/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    
    messages.value.push({ 
      role: 'system', 
      text: `CONSCIÊNCIA EXPANDIDA: O documento '${file.name}' foi injetado na categoria ${selectedCategory.value}.` 
    });
    isUploadModalOpen.value = false;
  } catch (error) {
    messages.value.push({ role: 'system', text: 'FALHA NO UPLOAD DE CONSCIÊNCIA.' });
  } finally {
    uploading.value = false;
    scrollToBottom();
  }
};

const sendMessage = async () => {
  if (!newMessage.value.trim() || loading.value) return;

  const userText = newMessage.value;
  messages.value.push({ role: 'user', text: userText });
  newMessage.value = '';
  loading.value = true;
  scrollToBottom();

  try {
    const response = await api.post('/chat/message', { message: userText });
    messages.value.push({ role: 'ai', text: response.data.response, canSave: true });
  } catch (error) {
    messages.value.push({ role: 'system', text: 'ERRO CRÍTICO: FALHA NA CONEXÃO COM O ESTRATEGISTA.' });
  } finally {
    loading.value = false;
    scrollToBottom();
  }
};

const triggerRadar = async () => {
  loading.value = true;
  messages.value.push({ role: 'system', text: 'INICIANDO VARREDURA DE RADAR... ACESSANDO ADS LIBRARY...' });
  scrollToBottom();

  try {
    const response = await api.post('/radar/scan', { page_id: "418295661555191" });
    messages.value.push({ 
      role: 'radar_alert', 
      text: response.data.tactical_alert 
    });
  } catch (error) {
    messages.value.push({ role: 'system', text: 'FALHA NO RADAR: PERÍMETRO BLOQUEADO OU ERRO DE CONEXÃO.' });
  } finally {
    loading.value = false;
    scrollToBottom();
  }
};

const triggerFileInput = () => {
  fileInput.value.click();
};

const handleCreativeUpload = async (event) => {
  const file = event.target.files[0];
  if (!file) return;

  messages.value.push({ role: 'user', text: `Analisando criativo: ${file.filename || file.name}` });
  loading.value = true;
  scrollToBottom();

  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await api.post('/brain/analyze-creative', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    const analysisText = JSON.stringify(response.data.analysis, null, 2);
    messages.value.push({ 
      role: 'ai', 
      text: `ANÁLISE DE CRIATIVO CONCLUÍDA:\n${analysisText}`,
      canSave: true 
    });
  } catch (error) {
    messages.value.push({ role: 'system', text: 'ERRO AO ANALISAR CRIATIVO.' });
  } finally {
    loading.value = false;
    scrollToBottom();
  }
};

const saveToObsidian = async (msg) => {
  try {
    await api.post('/brain/save-to-obsidian', {
      title: "Conversa Celebro",
      content: msg.text,
      tags: ["chat-memory"]
    });
    alert("MEMÓRIA PERSISTIDA NO OBSIDIAN.");
    msg.canSave = false;
  } catch (error) {
    alert("FALHA NA PERSISTÊNCIA.");
  }
};

onMounted(scrollToBottom);
</script>

<template>
  <div class="flex flex-col h-full bg-bracci-black text-[13px] font-mono border border-bracci-gold/20 shadow-2xl">
    <!-- Header do Terminal -->
    <div class="p-3 border-b border-bracci-gold/20 flex justify-between items-center bg-black/40">
      <div class="flex items-center gap-2">
        <div class="w-2 h-2 rounded-full bg-bracci-gold animate-pulse"></div>
        <span class="text-bracci-gold uppercase tracking-[0.2em] font-black">Celebro Cold Intelligence v2.1</span>
      </div>
      <div class="flex items-center gap-4">
        <button @click="triggerRadar" class="text-[9px] bg-red-950/40 border border-red-500/30 text-red-400 px-2 py-1 hover:bg-red-500 hover:text-white transition-all uppercase font-black">
          Radar de Inimigos
        </button>
        <span class="text-[9px] opacity-40 uppercase">Safe Connection: ACTIVE</span>
      </div>
    </div>

    <!-- Mensagens -->
    <div 
      ref="chatContainer"
      class="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin scrollbar-thumb-bracci-gold/20"
    >
      <div v-for="(msg, index) in messages" :key="index" :class="[
        'flex flex-col max-w-[85%]',
        msg.role === 'user' ? 'ml-auto items-end' : 'items-start'
      ]">
        <div :class="[
          'p-4 rounded-sm border leading-relaxed relative group',
          msg.role === 'user' ? 'bg-white/5 border-white/10 text-white' : 
          msg.role === 'ai' ? 'bg-bracci-gold/5 border-bracci-gold/30 text-bracci-gold' : 
          msg.role === 'radar_alert' ? 'bg-red-500/10 border-red-500/40 text-red-200 border-l-4 shadow-[0_0_20px_rgba(239,68,68,0.1)]' :
          'bg-red-500/5 border-red-500/20 text-red-400 text-[11px]'
        ]">
          <span v-if="msg.role === 'ai'" class="block mb-2 text-[9px] opacity-50 uppercase font-black">Estrategista:</span>
          <span v-if="msg.role === 'user'" class="block mb-2 text-[9px] opacity-50 uppercase font-black">Comando:</span>
          <span v-if="msg.role === 'radar_alert'" class="block mb-2 text-[10px] text-red-500 uppercase font-black tracking-widest animate-pulse">⚠️ ALERTA TÁTICO: INTELIGÊNCIA COMPETITIVA</span>
          
          <pre class="whitespace-pre-wrap font-mono">{{ msg.text }}</pre>
          
          <button 
            v-if="msg.canSave"
            @click="saveToObsidian(msg)"
            class="mt-4 text-[8px] border border-bracci-gold/40 px-2 py-1 hover:bg-bracci-gold hover:text-bracci-black transition-all uppercase font-black"
          >
            💾 Salvar no Obsidian
          </button>
        </div>
      </div>

      <div v-if="loading" class="flex items-center gap-2 text-bracci-gold animate-pulse">
        <span class="text-[10px] uppercase font-black">Processando Variáveis de Defesa...</span>
      </div>
    </div>

    <!-- Input Fixo -->
    <div class="p-6 bg-black/60 border-t border-bracci-gold/10">
      <div class="flex gap-4 items-center">
        <div class="flex gap-2">
          <button 
            @click="triggerFileInput"
            class="text-bracci-gold/60 hover:text-bracci-gold transition-colors text-xl"
            title="Analisar Criativo"
          >
            📎
          </button>
          <button 
            @click="toggleUploadModal"
            class="text-bracci-gold/60 hover:text-bracci-gold transition-colors text-xl"
            title="Upload de Consciência"
          >
            🧠
          </button>
        </div>
        
        <input 
          type="file" 
          ref="fileInput" 
          class="hidden" 
          @change="handleCreativeUpload" 
          accept="image/*,video/*" 
        />

        <div class="relative flex-1 group">
          <input 
            v-model="newMessage"
            @keyup.enter="sendMessage"
            type="text"
            placeholder="Digite seu comando tático..."
            class="w-full bg-transparent border-b border-bracci-gold/30 p-4 outline-none text-white focus:border-bracci-gold transition-all placeholder:text-white/20 uppercase text-xs"
          />
          <div class="absolute right-4 top-4 text-[10px] text-bracci-gold opacity-30 group-focus-within:opacity-100 transition-opacity">
            EXECUTE
          </div>
        </div>
      </div>
    </div>

    <!-- Modal de Upload de Consciência -->
    <div v-if="isUploadModalOpen" class="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div class="bg-bracci-black border border-bracci-gold/40 w-full max-w-md shadow-[0_0_50px_rgba(197,160,89,0.1)]">
        <div class="p-4 border-b border-bracci-gold/20 flex justify-between items-center bg-bracci-gold/5">
          <h3 class="text-bracci-gold font-black uppercase tracking-tighter text-sm">Upload de Consciência</h3>
          <button @click="toggleUploadModal" class="text-bracci-gold hover:text-white">✕</button>
        </div>
        
        <div class="p-6 space-y-6">
          <div class="space-y-2">
            <label class="text-[10px] text-bracci-gold/60 uppercase font-black">Categoria da Memória</label>
            <select 
              v-model="selectedCategory"
              class="w-full bg-black border border-bracci-gold/20 p-3 text-bracci-gold outline-none focus:border-bracci-gold transition-all appearance-none uppercase text-xs"
            >
              <option value="BRANDING">Branding (Manual de Marca)</option>
              <option value="MARKETING">Marketing (Estratégias)</option>
              <option value="HISTORICO">Histórico (Dados Passados)</option>
            </select>
          </div>

          <div class="space-y-2">
            <label class="text-[10px] text-bracci-gold/60 uppercase font-black">Documento (.pdf ou .txt)</label>
            <div 
              @click="$refs.brainFileInput.click()"
              class="border-2 border-dashed border-bracci-gold/20 p-8 text-center cursor-pointer hover:border-bracci-gold/40 transition-all group"
            >
              <input 
                type="file" 
                ref="brainFileInput" 
                class="hidden" 
                @change="handleBrainUpload" 
                accept=".pdf,.txt" 
              />
              <div v-if="!uploading" class="space-y-2">
                <div class="text-2xl opacity-40 group-hover:opacity-100 transition-opacity">📄</div>
                <p class="text-[10px] text-white/40 uppercase">Clique para selecionar ou arraste o arquivo</p>
              </div>
              <div v-else class="flex flex-col items-center gap-2">
                <div class="w-6 h-6 border-2 border-bracci-gold border-t-transparent rounded-full animate-spin"></div>
                <p class="text-[10px] text-bracci-gold animate-pulse font-black uppercase">Injetando Conhecimento...</p>
              </div>
            </div>
          </div>
        </div>

        <div class="p-4 bg-black/40 text-[9px] text-bracci-gold/40 uppercase text-center border-t border-bracci-gold/10">
          A IA Celebro processará estes dados como Contexto de Longo Prazo.
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.scrollbar-thin::-webkit-scrollbar {
  width: 4px;
}
.scrollbar-thin::-webkit-scrollbar-track {
  background: transparent;
}
.scrollbar-thin::-webkit-scrollbar-thumb {
  background: rgba(197, 160, 89, 0.2);
}
</style>
