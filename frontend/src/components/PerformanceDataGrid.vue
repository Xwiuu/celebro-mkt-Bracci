<script setup>
const props = defineProps({
  campaigns: { type: Array, default: () => [] }
});

const formatBRL = (val) => {
  return (Number(val) || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 });
};
</script>

<template>
  <div class="space-y-12 pb-20">
    <div class="flex justify-between items-end border-b border-gray-100 pb-6">
      <div class="border-l-4 border-bracci-gold pl-6">
        <h3 class="text-[10px] font-black uppercase tracking-[0.4em] italic text-gray-400 mb-2">
          Inventário de Performance Real-Time
        </h3>
        <p class="text-3xl font-black text-bracci-black tracking-tighter uppercase italic">
          Delta <span class="text-bracci-gold">Campaigns</span>
        </p>
      </div>
      <div class="text-right">
        <p class="text-[8px] font-bold text-gray-300 uppercase tracking-widest mb-1">Status do Panteão</p>
        <p class="text-xs font-mono text-bracci-black">{{ campaigns.length }} Ativos Operacionais</p>
      </div>
    </div>

    <!-- Tabela de Campanhas com Scroll -->
    <div class="bg-white border-thin border-gray-100 shadow-soft overflow-hidden">
      <div class="overflow-x-auto max-h-[600px] scrollbar-thin scrollbar-thumb-bracci-gold/20">
        <table class="w-full text-left border-collapse">
          <thead class="bg-gray-50 sticky top-0 z-10">
            <tr>
              <th class="p-6 text-[10px] font-black uppercase tracking-widest text-gray-400 border-b border-gray-100">Campanha</th>
              <th class="p-6 text-[10px] font-black uppercase tracking-widest text-gray-400 border-b border-gray-100">Plataforma</th>
              <th class="p-6 text-[10px] font-black uppercase tracking-widest text-gray-400 border-b border-gray-100 text-right">Gasto Real (Spend)</th>
              <th class="p-6 text-[10px] font-black uppercase tracking-widest text-gray-400 border-b border-gray-100 text-right">ROAS</th>
              <th class="p-6 text-[10px] font-black uppercase tracking-widest text-gray-400 border-b border-gray-100 text-right">CPA</th>
              <th class="p-6 text-[10px] font-black uppercase tracking-widest text-gray-400 border-b border-gray-100 text-center">Status</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-for="campaign in campaigns" :key="campaign.id" class="hover:bg-gray-50/50 transition-colors group">
              <td class="p-6">
                <!-- TAREFA: Usar campanha.nome conforme backend -->
                <p class="text-sm font-bold text-bracci-black uppercase tracking-tight group-hover:text-bracci-gold transition-colors">
                  {{ campaign.nome || campaign.name }}
                </p>
              </td>
              <td class="p-6">
                <span class="text-[9px] font-black bg-gray-100 px-2 py-1 text-gray-500 uppercase tracking-widest">
                  {{ campaign.plataforma || 'META' }}
                </span>
              </td>
              <td class="p-6 text-right font-mono text-sm text-gray-600">
                <!-- TAREFA 4: Exibir Gasto Real com Fallback Blindado (Prioridade: investimento_total) -->
                {{ formatBRL(Number(campaign.investimento_total || campaign.spend || campaign.investimento || (campaign.investimento_diario ? campaign.investimento_diario * 30 : 0))) }}
              </td>
              <td class="p-6 text-right">
                <span :class="['font-black italic text-lg tracking-tighter', (Number(campaign.roas) || 0) > 4 ? 'text-bracci-gold' : 'text-bracci-black']">
                  {{ (Number(campaign.roas) || 0).toFixed(2) }}x
                </span>
              </td>
              <td class="p-6 text-right font-mono text-sm text-gray-600">
                <!-- TAREFA: Usar cpa do backend -->
                {{ formatBRL(campaign.cpa) }}
              </td>
              <td class="p-6 text-center">
                <div class="flex justify-center">
                  <div :class="['w-2 h-2 rounded-full', campaign.status === 'ACTIVE' || campaign.status === 'ativa' ? 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.4)]' : 'bg-gray-300']"></div>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="campaigns.length === 0" class="py-40 border-2 border-dashed border-gray-100 flex flex-col items-center justify-center space-y-6">
      <div class="w-12 h-12 border-4 border-bracci-gold border-t-transparent animate-spin rounded-full"></div>
      <p class="text-[10px] font-black uppercase tracking-[0.5em] text-gray-300 animate-pulse">
        Sincronizando Ativos com Meta Ads API...
      </p>
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
.shadow-soft {
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.02);
}
</style>
