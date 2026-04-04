<script setup>
import { computed } from 'vue';

const props = defineProps({
  campaign: { type: Object, required: true }
});

const emit = defineEmits(['analyze', 'open-generator']);
const latestDecision = computed(() => props.campaign.latest_decision);

const actionStyles = computed(() => {
  const action = latestDecision.value?.acao_sugerida;
  const styles = {
    'ESCALAR': 'bg-green-50 text-green-800',
    'PAUSAR': 'bg-red-50 text-red-800',
    'MANTER': 'bg-amber-50 text-amber-800',
    'TROCAR_CRIATIVO': 'bg-bracci-offwhite border-thin border-bracci-gold text-bracci-gold'
  };
  return styles[action] || 'bg-gray-50 text-gray-400';
});
</script>

<template>
  <div class="bg-white border-thin border-gray-100 p-10 shadow-[0_4px_30px_rgba(0,0,0,0.02)] flex flex-col h-full transition-all hover:shadow-[0_10px_50px_rgba(0,0,0,0.05)] hover:-translate-y-1">
    <div class="mb-12">
      <h3 class="text-xl font-bold text-bracci-black tracking-tight-luxury uppercase mb-1">{{ campaign.nome }}</h3>
      <p class="text-[9px] text-gray-400 uppercase tracking-widest font-light">{{ campaign.plataforma }} Platform</p>
    </div>

    <div class="grid grid-cols-3 gap-6 mb-16">
      <div class="space-y-2">
        <p class="text-[8px] text-gray-300 uppercase tracking-widest font-bold">ROAS</p>
        <p class="text-2xl font-light" :class="campaign.roas > 4 ? 'text-bracci-gold font-bold' : 'text-bracci-black'">
          {{ campaign.roas.toFixed(2) }}x
        </p>
      </div>
      <div class="space-y-2">
        <p class="text-[8px] text-gray-300 uppercase tracking-widest font-bold">INVESTIMENTO</p>
        <p class="text-2xl font-light text-bracci-black">
          {{ (campaign.investimento_diario * 30).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 }) }}
        </p>
      </div>
      <div class="space-y-2">
        <p class="text-[8px] text-gray-300 uppercase tracking-widest font-bold">CPA</p>
        <p class="text-2xl font-light text-bracci-black">
          {{ campaign.cpa.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 }) }}
        </p>
      </div>
    </div>

    <div class="mt-auto">
      <div v-if="latestDecision" class="p-8 rounded-sm transition-all" :class="actionStyles">
        <div class="flex items-center justify-between mb-4 border-b border-inherit/20 pb-2">
          <span class="text-[8px] font-extrabold uppercase tracking-widest opacity-60 italic">AI Oracle Recommendation</span>
          <span class="text-[9px] font-black uppercase tracking-widest">{{ latestDecision.acao_sugerida }}</span>
        </div>
        <p class="text-[11px] leading-relaxed text-bracci-black/70 font-light italic">
          "{{ latestDecision.justificativa_ia }}"
        </p>

        <button 
          v-if="latestDecision.acao_sugerida === 'TROCAR_CRIATIVO'"
          @click="emit('open-generator', campaign.id)"
          class="w-full mt-8 bg-bracci-gold text-white text-[10px] font-extrabold uppercase tracking-luxury py-4 transition-all hover:bg-bracci-black"
        >
          Generate Elite Creative
        </button>
      </div>
      
      <div v-else class="py-8 border-thin border-dashed border-gray-100 text-center flex flex-col items-center">
        <p class="text-[9px] text-gray-300 italic tracking-widest font-light">Oracle Waiting Protocol</p>
      </div>
    </div>
  </div>
</template>
