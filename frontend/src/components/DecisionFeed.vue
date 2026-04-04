<script setup>
import { ref } from 'vue';

const props = defineProps({
  decisions: { type: Array, default: () => [] },
  loading: Boolean
});

const emit = defineEmits(['approve', 'reject']);
</script>

<template>
  <div class="bg-white border-thin border-gray-100 p-10 shadow-sm h-full flex flex-col">
    <div class="flex items-center justify-between mb-12">
      <h3 class="text-[11px] font-black uppercase tracking-luxury italic border-l-4 border-bracci-gold pl-6">
        Centro de Comando IA
      </h3>
      <div v-if="loading" class="flex items-center gap-2">
        <span class="w-2 h-2 bg-bracci-gold rounded-full animate-ping"></span>
        <span class="text-[8px] text-bracci-gold font-bold uppercase tracking-widest">Neuro-Sócio Processando</span>
      </div>
    </div>

    <div class="flex-1 space-y-8 overflow-y-auto pr-4">
      <div v-for="decision in decisions" :key="decision.id" 
           class="group relative bg-bracci-offwhite border-thin border-gray-100 p-8 hover:border-bracci-gold transition-all">
        
        <div class="flex justify-between items-start mb-6">
          <span class="text-[9px] font-black uppercase tracking-widest px-2 py-1 bg-bracci-matte text-white italic">
            {{ decision.tipo_acao }}
          </span>
          <p class="text-[10px] text-green-600 font-bold uppercase tracking-widest italic">
            + R$ {{ decision.impacto_estimado.toLocaleString() }} est.
          </p>
        </div>

        <p class="text-[11px] leading-relaxed text-bracci-matte/70 font-light italic mb-8 border-l-2 border-bracci-gold/20 pl-4">
          "{{ decision.justificativa_neuro }}"
        </p>

        <div class="flex gap-4">
          <button @click="emit('approve', decision.id)" 
                  class="flex-1 bg-bracci-gold text-white text-[9px] font-bold uppercase tracking-widest py-3 hover:bg-bracci-matte transition-all shadow-lg shadow-bracci-gold/10">
            Aprovar Intervenção
          </button>
          <button @click="emit('reject', decision.id)" 
                  class="px-6 border-thin border-gray-200 text-[9px] font-bold uppercase tracking-widest hover:bg-red-50 hover:text-red-500 transition-all text-gray-400">
            Rejeitar
          </button>
        </div>
      </div>

      <div v-if="!decisions.length && !loading" class="h-64 flex flex-col items-center justify-center border-thin border-dashed border-gray-100">
        <p class="text-[10px] text-gray-300 italic tracking-widest">Monitorando fluxo de dados... Nenhuma intervenção necessária.</p>
      </div>
    </div>

    <div class="mt-12 pt-8 border-t border-gray-50 flex justify-between items-center opacity-40">
      <p class="text-[8px] tracking-luxury uppercase font-bold italic">Standard: Neuro-Estratégia Bunker</p>
      <div class="flex gap-1">
        <span class="w-1 h-1 bg-bracci-gold rounded-full"></span>
        <span class="w-1 h-1 bg-bracci-gold rounded-full opacity-50"></span>
        <span class="w-1 h-1 bg-bracci-gold rounded-full opacity-20"></span>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Efeito de Glow Bunker no Card Selecionado */
.border-bracci-gold {
  box-shadow: 0 0 30px rgba(197, 160, 89, 0.05);
}
</style>
