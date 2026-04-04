<script setup>
import { ref, onMounted, nextTick } from 'vue';
import api from '../services/api';

const messages = ref([
  { role: 'ai', text: 'MESA DE NEGOCIAÇÃO ATIVA. Informe o budget e os objetivos da semana para iniciarmos o debate tático.' }
]);
const newMessage = ref('');
const livePlan = ref('');
const loading = ref(false);
const chatContainer = ref(null);

const scrollToBottom = async () => {
  await nextTick();
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
  }
};

const negotiate = async () => {
  if (!newMessage.value.trim() || loading.value) return;

  const userText = newMessage.value;
  messages.value.push({ role: 'user', text: userText });
  newMessage.value = '';
  loading.value = true;
  scrollToBottom();

  try {
    const history = messages.value.slice(1, -1).map(m => ({ role: m.role, content: m.text }));
    const response = await api.post('/war-room/negotiate', { 
      message: userText,
      history: history
    });
    
    messages.value.push({ role: 'ai', text: response.data.response });
    
    // Tenta extrair um esboço de plano se a IA enviou algo estruturado
    // Por enquanto, apenas atualizamos o livePlan se o usuário quiser editar manualmente
  } catch (error) {
    messages.value.push({ role: 'ai', text: 'ERRO NA COMUNICAÇÃO TÁTICA.' });
  } finally {
    loading.value = false;
    scrollToBottom();
  }
};

const sanctionPlan = async () => {
  if (!livePlan.value.trim()) {
    alert("O DOCUMENTO VIVO ESTÁ VAZIO. DEFINA O PLANO ANTES DE SANCIONAR.");
    return;
  }

  try {
    loading.value = true;
    const summary = messages.value.filter(m => m.role !== 'system').map(m => `${m.role.toUpperCase()}: ${m.text}`).join('\n');
    const response = await api.post('/war-room/sanction', {
      final_plan: livePlan.value,
      summary: summary
    });
    alert(response.data.message);
  } catch (error) {
    alert("FALHA AO SANCIONAR: " + error.message);
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="h-full flex flex-col space-y-4 animate-fade-in">
    <header class="flex justify-between items-center border-b border-bracci-gold/20 pb-4">
      <div>
        <h2 class="text-2xl font-light tracking-[0.2em] text-white">Mesa de <span class="text-bracci-gold font-black">NEGOCIAÇÃO</span></h2>
        <p class="text-[9px] uppercase tracking-[0.4em] opacity-40">Tactical Strategy Debate & Sanctioning</p>
      </div>
      <div class="flex items-center gap-4">
        <div class="text-right">
          <p class="text-[8px] uppercase opacity-40">Status do Cofre</p>
          <p class="text-[10px] text-green-500 font-mono">OBSIDIAN CONNECTED</p>
        </div>
      </div>
    </header>

    <div class="flex-1 flex gap-6 overflow-hidden">
      <!-- Lado Esquerdo: Chat Tático -->
      <div class="w-1/2 flex flex-col bg-black/40 border border-white/5 rounded-sm overflow-hidden">
        <div class="p-3 border-b border-white/5 bg-white/5 flex justify-between items-center">
          <span class="text-[9px] font-black uppercase tracking-widest opacity-60">Debate de Performance</span>
          <div class="flex gap-1">
            <div class="w-1 h-1 bg-bracci-gold rounded-full"></div>
            <div class="w-1 h-1 bg-bracci-gold rounded-full"></div>
          </div>
        </div>

        <div 
          ref="chatContainer"
          class="flex-1 overflow-y-auto p-4 space-y-4 font-mono text-[12px] scrollbar-thin scrollbar-thumb-bracci-gold/10"
        >
          <div v-for="(msg, index) in messages" :key="index" :class="[
            'p-3 border leading-relaxed',
            msg.role === 'user' ? 'bg-white/5 border-white/10 text-white ml-8' : 'bg-bracci-gold/5 border-bracci-gold/20 text-bracci-gold mr-8'
          ]">
            <span class="block mb-1 text-[8px] opacity-50 uppercase font-black">{{ msg.role === 'ai' ? 'Estrategista' : 'Comando' }}:</span>
            {{ msg.text }}
          </div>
        </div>

        <div class="p-4 bg-black/60 border-t border-white/5">
          <input 
            v-model="newMessage"
            @keyup.enter="negotiate"
            type="text"
            placeholder="Argumentar estratégia..."
            class="w-full bg-transparent border-b border-bracci-gold/20 p-2 outline-none text-white focus:border-bracci-gold transition-all uppercase text-[10px]"
          />
        </div>
      </div>

      <!-- Lado Direito: Live Document -->
      <div class="w-1/2 flex flex-col bg-white/5 border border-white/10 rounded-sm">
        <div class="p-3 border-b border-white/10 bg-bracci-gold/5 flex justify-between items-center">
          <span class="text-[9px] font-black uppercase tracking-widest text-bracci-gold">Documento Vivo: Plano de Batalha</span>
          <span class="text-[8px] opacity-40">EDITÁVEL</span>
        </div>

        <div class="flex-1 p-6">
          <textarea 
            v-model="livePlan"
            placeholder="O esboço do plano aparecerá aqui ou pode ser redigido manualmente após o debate..."
            class="w-full h-full bg-transparent outline-none text-white font-light italic text-sm leading-relaxed resize-none placeholder:opacity-20"
          ></textarea>
        </div>

        <div class="p-6 border-t border-white/10">
          <button 
            @click="sanctionPlan"
            :disabled="loading"
            class="w-full group relative overflow-hidden bg-transparent border-2 border-bracci-gold py-4 transition-all hover:bg-bracci-gold active:scale-[0.98]"
          >
            <div class="absolute inset-0 bg-bracci-gold opacity-0 group-hover:opacity-10 transition-opacity"></div>
            <span class="relative z-10 text-bracci-gold group-hover:text-bracci-black font-black uppercase tracking-[0.6em] text-xs">
              [ SANCIONAR PLANO ]
            </span>
            <!-- Glow Effect -->
            <div class="absolute inset-0 shadow-[0_0_20px_rgba(197,160,89,0.3)] opacity-0 group-hover:opacity-100 transition-opacity"></div>
          </button>
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
  background: rgba(197, 160, 89, 0.1);
}
.animate-fade-in {
  animation: fadeIn 0.5s ease-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
