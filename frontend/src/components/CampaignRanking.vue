<script setup>
import { computed } from 'vue';
import { Bar } from 'vue-chartjs';
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const props = defineProps({
  stats: {
    type: Object,
    required: true,
    // Garante que se o backend demorar, o app não quebra
    default: () => ({ ranking: [] }) 
  }
});

// Formata pra Reais (R$)
const formatBRL = (value) => {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
};

const chartData = computed(() => {
  const ranking = props.stats?.ranking || [];

  return {
    labels: ranking.map(item => {
      const id = item.name.toString();
      return id.length > 10 ? `ID: ...${id.slice(-5)}` : id;
    }),
    datasets: [
      {
        label: 'Faturamento',
        // 🚨 AGORA A BARRA É O FATURAMENTO (REVENUE) E NÃO O ROAS
        data: ranking.map(item => item.revenue),
        backgroundColor: ranking.map(item => 
          item.platform.toLowerCase().includes('meta') ? '#1877F2' : '#C5A059'
        ),
        borderRadius: 4,
        barThickness: 20,
      }
    ]
  };
});

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  indexAxis: 'y', 
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: '#000000',
      titleColor: '#A0A0A0',
      bodyColor: '#C5A059',
      titleFont: { size: 10, weight: 'bold' },
      bodyFont: { size: 14, weight: 'black' },
      padding: 12,
      cornerRadius: 4,
      callbacks: {
        // Mostra o Faturamento e o ROAS no quadradinho preto!
        label: (context) => {
          const item = props.stats.ranking[context.dataIndex];
          return [
            ` Faturamento: ${formatBRL(item.revenue)}`,
            ` ROAS: ${item.roas}x`
          ];
        }
      }
    }
  },
  scales: {
    x: { 
      beginAtZero: true, 
      grid: { display: false },
      ticks: { 
        font: { size: 10, weight: 'bold' }, 
        color: '#A0A0A0',
        // Oculta os números do eixo X embaixo para ficar mais clean
        display: false 
      }
    },
    y: { 
      grid: { display: false },
      ticks: { font: { size: 11, weight: 'bold' }, color: '#333333' }
    }
  }
};
</script>

<template>
  <div class="relative w-full h-full">
    
    <div class="flex justify-between items-start mb-8">
      <div>
        <h3 class="text-[9px] font-black uppercase tracking-[0.3em] text-gray-400 mb-1">Asset Performance</h3>
        <h2 class="text-xl font-black text-black tracking-tighter uppercase italic">Ranking Omnichannel</h2>
      </div>

      <div class="flex gap-4">
        <div class="flex items-center gap-2">
          <div class="w-3 h-3 bg-[#1877F2] rounded-sm"></div>
          <span class="text-[9px] font-bold text-gray-500 uppercase tracking-widest">Meta Ads</span>
        </div>
        <div class="flex items-center gap-2">
          <div class="w-3 h-3 bg-[#C5A059] rounded-sm"></div>
          <span class="text-[9px] font-bold text-gray-500 uppercase tracking-widest">Google Ads</span>
        </div>
      </div>
    </div>

    <div class="h-[350px] w-full">
      <Bar v-if="props.stats?.ranking?.length > 0" :data="chartData" :options="chartOptions" />
      
      <div v-else class="w-full h-full flex flex-col items-center justify-center border-2 border-dashed border-gray-100 rounded-lg">
        <span class="text-3xl mb-2">📊</span>
        <p class="text-[10px] font-bold uppercase tracking-widest text-gray-400">Sem dados de ranking no período</p>
      </div>
    </div>
    
  </div>
</template>

<style scoped>
/* O Tailwind já dá conta de tudo, mas se precisar de algum CSS extra, vai aqui */
</style>