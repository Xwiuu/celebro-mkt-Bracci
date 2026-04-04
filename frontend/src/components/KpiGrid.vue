<script setup>
const props = defineProps({
  stats: {
    type: Object,
    required: true,
    default: () => ({})
  }
});

// Funções de formatação blindadas para números diretos
const fCurrency = (val) => {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val || 0);
};

const fNumber = (val) => {
  return new Intl.NumberFormat('pt-BR').format(val || 0);
};

const fPercent = (val) => {
  return ((val || 0) * 100).toFixed(2) + '%';
};
</script>

<template>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
    
    <div class="luxury-card group">
      <p class="card-label">Faturamento Total</p>
      <div class="flex justify-between items-end mt-4">
        <h3 class="card-value">{{ fCurrency(stats.total_revenue) }}</h3>
        <div class="card-line"></div>
      </div>
    </div>

    <div class="luxury-card group">
      <p class="card-label">Investimento (Spend)</p>
      <div class="flex justify-between items-end mt-4">
        <h3 class="card-value">{{ fCurrency(stats.total_spend) }}</h3>
        <div class="card-line"></div>
      </div>
    </div>

    <div class="luxury-card group bg-black border-b-2 border-b-bracci-gold">
      <p class="card-label text-gray-500">ROAS Médio</p>
      <div class="flex justify-between items-end mt-4">
        <h3 class="card-value text-bracci-gold italic">{{ stats.total_roas?.toFixed(2) || '0.00' }}x</h3>
      </div>
    </div>

    <div class="luxury-card group">
      <p class="card-label">Cliques</p>
      <div class="flex justify-between items-end mt-4">
        <h3 class="card-value">{{ fNumber(stats.total_clicks) }}</h3>
        <div class="card-line"></div>
      </div>
    </div>

    <div class="luxury-card group">
      <p class="card-label">Impressões</p>
      <div class="flex justify-between items-end mt-4">
        <h3 class="card-value">{{ fNumber(stats.total_impressions) }}</h3>
        <div class="card-line"></div>
      </div>
    </div>

  </div>
</template>

<style scoped>
.luxury-card { @apply bg-white p-8 border border-gray-100 shadow-sm relative transition-all duration-500 hover:shadow-2xl hover:-translate-y-1; }
.card-label { @apply text-[9px] font-black text-gray-400 uppercase tracking-[0.3em] italic; }
.card-value { @apply text-3xl font-black text-black tracking-tighter leading-none; }
.card-line { @apply absolute bottom-0 left-0 h-[1px] w-0 bg-bracci-gold transition-all duration-700 group-hover:w-full; }
</style>