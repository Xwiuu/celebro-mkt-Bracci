<script setup>
import { computed } from 'vue';

// Recebe os dados de "stats" lá do ClientDashboard.vue
const props = defineProps({
  stats: {
    type: Object,
    required: true,
    default: () => ({
      total_revenue: 0,
      total_spend: 0,
      total_roas: 0,
      total_clicks: 0,
      total_impressions: 0
    })
  }
});

// Funções para formatar dinheiro e números grandes
const formatCurrency = (value) => {
  return new Intl.NumberFormat('pt-BR', { 
    style: 'currency', 
    currency: 'BRL' 
  }).format(value || 0);
};

const formatNumber = (value) => {
  return new Intl.NumberFormat('pt-BR').format(value || 0);
};
</script>

<template>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
    
    <div class="bg-white p-8 border border-gray-100 shadow-xl rounded-sm relative overflow-hidden group hover:border-green-400 transition-colors duration-300">
      <div class="absolute top-0 right-0 w-16 h-16 bg-green-50 rounded-bl-full -mr-8 -mt-8 transition-transform group-hover:scale-125"></div>
      <h3 class="text-[10px] font-black uppercase tracking-[0.2em] text-gray-400 mb-2 relative z-10">
        Captado Real
      </h3>
      <p class="text-3xl font-black text-black relative z-10">
        {{ formatCurrency(stats.total_revenue) }}
      </p>
    </div>

    <div class="bg-white p-8 border border-gray-100 shadow-xl rounded-sm relative overflow-hidden group hover:border-red-400 transition-colors duration-300">
      <div class="absolute top-0 right-0 w-16 h-16 bg-red-50 rounded-bl-full -mr-8 -mt-8 transition-transform group-hover:scale-125"></div>
      <h3 class="text-[10px] font-black uppercase tracking-[0.2em] text-gray-400 mb-2 relative z-10">
        Investimento
      </h3>
      <p class="text-3xl font-black text-black relative z-10">
        {{ formatCurrency(stats.total_spend) }}
      </p>
    </div>

    <div class="bg-white p-8 border border-bracci-gold/30 shadow-xl rounded-sm relative overflow-hidden group hover:border-bracci-gold transition-colors duration-300">
      <div class="absolute top-0 right-0 w-16 h-16 bg-bracci-gold/10 rounded-bl-full -mr-8 -mt-8 transition-transform group-hover:scale-125"></div>
      <h3 class="text-[10px] font-black uppercase tracking-[0.2em] text-gray-400 mb-2 relative z-10">
        ROAS Global
      </h3>
      <p class="text-3xl font-black text-bracci-gold relative z-10">
        {{ (stats.total_roas || 0).toFixed(2) }}x
      </p>
    </div>

    <div class="bg-white p-8 border border-gray-100 shadow-xl rounded-sm relative overflow-hidden group hover:border-blue-400 transition-colors duration-300">
      <div class="absolute top-0 right-0 w-16 h-16 bg-blue-50 rounded-bl-full -mr-8 -mt-8 transition-transform group-hover:scale-125"></div>
      <h3 class="text-[10px] font-black uppercase tracking-[0.2em] text-gray-400 mb-2 relative z-10">
        Tráfego (Cliques)
      </h3>
      <p class="text-3xl font-black text-black relative z-10">
        {{ formatNumber(stats.total_clicks) }}
      </p>
      <p class="text-[9px] text-gray-400 mt-1 uppercase tracking-widest font-bold">
        Imps: {{ formatNumber(stats.total_impressions) }}
      </p>
    </div>

  </div>
</template>