<script setup>
import { ref, onMounted } from "vue";
import { RouterLink, RouterView } from "vue-router";
import api from "./services/api"; // 👈 Certifique-se que o caminho está correto

const canAccessNeuro = ref(false);
const isSidebarOpen = ref(true);

const checkNeuroAccess = async () => {
  try {
    // 🛡️ Pergunta ao Go se o seu IP é o do Mestre
    const response = await api.get("/neuro-socio/status");
    if (response.data && response.data.can_access) {
      canAccessNeuro.value = true;
      console.log("🧠 NeuroGuard: Acesso de elite detectado. Bem-vindo, Mestre.");
    }
  } catch (error) {
    // Se der erro 403 (IP negado), o botão continua invisível
    canAccessNeuro.value = false;
    console.warn("🛡️ NeuroGuard: Funcionalidades restritas ocultadas.");
  }
};

onMounted(() => {
  checkNeuroAccess();
});
</script>

<template>
  <div class="flex min-h-screen bg-[#FAFAFA] font-sans">
    <aside 
      class="bg-black text-white w-72 flex-shrink-0 transition-all duration-300 flex flex-col border-r border-white/5 shadow-2xl"
      :class="{ '-ml-72': !isSidebarOpen }"
    >
      <div class="p-10">
        <h1 class="text-2xl font-black tracking-tighter uppercase italic text-bracci-gold">
          Synxia <span class="text-white not-italic">OS</span>
        </h1>
        <p class="text-[8px] font-mono text-gray-500 uppercase tracking-[0.3em] mt-2">Intelligence Protocol v3.0</p>
      </div>

      <nav class="flex-1 px-6 space-y-2">
        <RouterLink 
          to="/" 
          class="flex items-center gap-4 px-4 py-4 rounded-sm text-[10px] font-black uppercase tracking-widest transition-all hover:bg-white/5 group"
          active-class="bg-white/10 text-bracci-gold border-l-2 border-bracci-gold"
        >
          <span class="opacity-50 group-hover:opacity-100">📊</span> Dashboard
        </RouterLink>

        <RouterLink 
          to="/comparative" 
          class="flex items-center gap-4 px-4 py-4 rounded-sm text-[10px] font-black uppercase tracking-widest transition-all hover:bg-white/5 group"
          active-class="bg-white/10 text-bracci-gold border-l-2 border-bracci-gold"
        >
          <span class="opacity-50 group-hover:opacity-100">↗️</span> Delta Analysis
        </RouterLink>

        <RouterLink 
          v-if="canAccessNeuro" 
          to="/neuro-socio" 
          class="flex items-center gap-4 px-4 py-4 rounded-sm text-[10px] font-black uppercase tracking-widest transition-all bg-bracci-gold/10 text-bracci-gold border border-bracci-gold/20 hover:bg-bracci-gold hover:text-black mt-10 animate-fade-in"
        >
          <span class="animate-pulse">🧠</span> Neuro-Sócio IA
        </RouterLink>
      </nav>

      <div class="p-8 border-t border-white/5">
        <div class="flex items-center gap-3">
          <div class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
          <span class="text-[9px] font-mono text-gray-500 uppercase tracking-widest">System Online</span>
        </div>
      </div>
    </aside>

    <main class="flex-1 overflow-y-auto">
      <button 
        @click="isSidebarOpen = !isSidebarOpen"
        class="fixed bottom-6 left-6 z-50 bg-black text-white p-3 rounded-full shadow-2xl hover:bg-bracci-gold transition-colors"
      >
        {{ isSidebarOpen ? '⬅️' : '➡️' }}
      </button>

      <RouterView />
    </main>
  </div>
</template>

<style>
/* Reset básico para o visual de luxo */
body {
  margin: 0;
  -webkit-font-smoothing: antialiased;
}

.animate-fade-in {
  animation: fadeIn 0.8s ease-out forwards;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateX(-10px); }
  to { opacity: 1; transform: translateX(0); }
}

/* Esconde scrollbar sem perder funcionalidade */
::-webkit-scrollbar {
  width: 0px;
  background: transparent;
}
</style>