<script setup>
import { ref, onMounted } from 'vue';
import api from '../services/api';
import CelebroChat from '../components/CelebroChat.vue';
import WarRoom from '../components/WarRoom.vue';
import CampaignCard from '../components/CampaignCard.vue';

const currentView = ref('terminal'); // terminal, warroom, copy, ingestion, report
const campaigns = ref([]);
const loadingIA = ref(false);
const isDragging = ref(false);
const uploading = ref(false);

const sidebarItems = [
  { id: 'terminal', label: 'Terminal (Chat)', icon: '◈' },
  { id: 'warroom', label: 'War Room (Geral)', icon: '⚔' },
  { id: 'radar', label: 'Radar de Inimigos', icon: '🕵️‍♂️' },
  { id: 'copy', label: 'Fábrica de Copy', icon: '✎' },
  { id: 'ingestion', label: 'Importar Dados', icon: '⤓' },
  { id: 'report', label: 'Report EOD', icon: '📊' }
];

const fetchBackend = async () => {
  try {
    const response = await api.get('/campaigns/');
    campaigns.value = response.data;
  } catch (error) {
    console.error(error);
  }
};

const handleFileUpload = async (event) => {
  const file = event.target.files?.[0] || event.dataTransfer?.files?.[0];
  if (!file) return;

  const formData = new FormData();
  formData.append('file', file);

  try {
    uploading.value = true;
    const response = await api.post('/import/csv', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    alert("SYSTEM: " + response.data.message);
    fetchBackend();
  } catch (error) {
    alert("CRITICAL_ERROR: " + (error.response?.data?.detail || "Protocol Failure"));
  } finally {
    uploading.value = false;
    isDragging.value = false;
  }
};

onMounted(fetchBackend);
</script>

<template>
  <div class="flex h-screen bg-bracci-black text-white overflow-hidden">
    <!-- Sidebar Esquerda Cyber -->
    <aside class="w-64 border-r border-bracci-gold/10 flex flex-col bg-black/40">
      <div class="p-8 border-b border-bracci-gold/10">
        <h2 class="text-xl font-black tracking-luxury text-bracci-gold">CELEBRO</h2>
        <p class="text-[9px] opacity-40 uppercase tracking-[0.3em]">Ambiente de Execução</p>
      </div>

      <nav class="flex-1 p-4 space-y-2">
        <button 
          v-for="item in sidebarItems" 
          :key="item.id"
          @click="currentView = item.id"
          class="w-full text-left p-4 rounded-sm transition-all flex items-center gap-4 group"
          :class="currentView === item.id ? 'bg-bracci-gold/10 text-bracci-gold border-l-2 border-bracci-gold' : 'hover:bg-white/5 text-white/60'"
        >
          <span class="text-lg opacity-50 group-hover:opacity-100">{{ item.icon }}</span>
          <span class="text-[10px] font-black uppercase tracking-widest">{{ item.label }}</span>
        </button>
      </nav>

      <div class="p-8 border-t border-bracci-gold/10">
        <div class="flex items-center gap-3">
          <div class="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_10px_rgba(34,197,94,0.5)]"></div>
          <span class="text-[9px] uppercase font-bold opacity-60">Status: Operacional</span>
        </div>
      </div>
    </aside>

    <!-- Área Central Dinâmica -->
    <main class="flex-1 flex flex-col relative">
      <!-- Background Cyber Grid -->
      <div class="absolute inset-0 opacity-[0.03] pointer-events-none bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')]"></div>

      <!-- Header -->
      <header class="h-20 border-b border-bracci-gold/10 flex items-center justify-between px-12 bg-black/20 backdrop-blur-md z-10">
        <div>
          <h1 class="text-[10px] font-black uppercase tracking-[0.5em] text-bracci-gold">Comando Central</h1>
          <p class="text-[9px] opacity-40 italic">Interface de Inteligência de Tráfego Frio</p>
        </div>
        <div class="flex gap-8">
          <div class="text-right">
            <p class="text-[9px] opacity-40 uppercase">Ativos Gerenciados</p>
            <p class="text-xs font-mono">{{ campaigns.length }} Campanhas</p>
          </div>
        </div>
      </header>

      <!-- Conteúdo Dinâmico -->
      <div class="flex-1 p-12 overflow-y-auto z-10">
        
        <!-- Terminal / Chat -->
        <div v-if="currentView === 'terminal'" class="h-full flex flex-col">
          <CelebroChat />
        </div>

        <!-- War Room -->
        <div v-if="currentView === 'warroom'" class="h-full">
          <WarRoom />
        </div>

        <!-- Radar de Inimigos -->
        <div v-if="currentView === 'radar'" class="h-full flex flex-col items-center justify-center space-y-8 animate-fade-in">
          <div class="text-6xl animate-pulse">🕵️‍♂️</div>
          <h2 class="text-2xl font-light tracking-[0.3em] uppercase">Módulo de Espionagem Ativo</h2>
          <p class="text-xs opacity-40 max-w-md text-center">O Radar de Inimigos monitora a Meta Ads Library em tempo real para detectar mudanças táticas na concorrência.</p>
          <button 
            @click="currentView = 'terminal'"
            class="border border-bracci-gold text-bracci-gold px-12 py-4 text-[10px] font-black uppercase tracking-[0.4em] hover:bg-bracci-gold hover:text-bracci-black transition-all"
          >
            Acessar Terminal para Varredura
          </button>
        </div>

        <!-- Fábrica de Copy -->
        <div v-if="currentView === 'copy'" class="space-y-8">
          <h2 class="text-2xl font-light italic">Fábrica de Copy <span class="text-bracci-gold font-bold not-italic font-sans">EM DESENVOLVIMENTO</span></h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-8 opacity-40 grayscale">
            <CampaignCard v-for="c in campaigns.slice(0, 2)" :key="c.id" :campaign="c" />
          </div>
        </div>

        <!-- Ingestion / Drag & Drop -->
        <div v-if="currentView === 'ingestion'" class="max-w-2xl mx-auto py-20">
          <section>
            <h3 class="text-[10px] font-black uppercase tracking-luxury mb-6 opacity-60 text-center">Data Ingestion Engine</h3>
            <div 
              @dragover.prevent="isDragging = true"
              @dragleave.prevent="isDragging = false"
              @drop.prevent="handleFileUpload"
              class="h-64 border-2 border-dashed flex flex-col items-center justify-center transition-all cursor-pointer relative overflow-hidden group bg-black/40"
              :class="isDragging ? 'border-bracci-gold bg-bracci-gold/5 shadow-[0_0_50px_rgba(197,160,89,0.1)]' : 'border-white/10'"
              @click="$refs.fileInput.click()"
            >
              <div v-if="uploading" class="flex flex-col items-center gap-6">
                <div class="w-12 h-12 border-4 border-bracci-gold border-t-transparent animate-spin rounded-full"></div>
                <p class="text-[11px] font-black uppercase tracking-[0.3em] text-bracci-gold animate-pulse">Injetando Dados no Postgres...</p>
              </div>
              <div v-else class="text-center">
                <div class="text-4xl mb-4 opacity-40">⤓</div>
                <p class="text-[12px] font-extrabold tracking-luxury uppercase text-white">Drop Raw CSV Export</p>
                <p class="text-[10px] text-bracci-gold/50 mt-2 tracking-widest italic uppercase">Meta Ads or Mlabs Protocol</p>
              </div>
              <input type="file" ref="fileInput" class="hidden" @change="handleFileUpload" accept=".csv" />
            </div>
          </section>
        </div>

        <!-- Report EOD -->
        <div v-if="currentView === 'report'" class="flex items-center justify-center h-full">
          <p class="text-[10px] font-black uppercase tracking-[0.5em] opacity-20 animate-pulse">Aguardando Fechamento do Dia para Gerar Report</p>
        </div>

      </div>
    </main>
  </div>
</template>

<style scoped>
.tracking-luxury {
  letter-spacing: 0.3em;
}
</style>
