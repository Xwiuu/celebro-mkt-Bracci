<script setup>
import { computed } from "vue";
import { Line } from "vue-chartjs";
import {
  Chart as ChartJS, Title, Tooltip, Legend, LineElement, LinearScale, PointElement, CategoryScale, Filler
} from "chart.js";

ChartJS.register(Title, Tooltip, Legend, LineElement, LinearScale, PointElement, CategoryScale, Filler);

const props = defineProps({
  chartData: { type: Object, required: true }
});

const options = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: { mode: 'index', intersect: false },
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: 'rgba(0,0,0,0.9)',
      padding: 12,
      bodyFont: { size: 12 },
      callbacks: {
        label: (context) => `${context.dataset.label}: R$ ${context.parsed.y.toLocaleString('pt-BR')}`
      }
    }
  },
  scales: {
    x: {
      grid: { display: false },
      ticks: { color: "#475569", font: { size: 9 }, maxTicksLimit: 8 }
    },
    // 🔵 Eixo da Esquerda (Meta Ads)
    y: {
      type: 'linear',
      display: true,
      position: 'left',
      beginAtZero: true,
      grid: { color: "rgba(255, 255, 255, 0.05)", drawBorder: false },
      ticks: { color: "#1877F2", font: { size: 9, weight: 'bold' } }
    },
    // 🟡 Eixo da Direita (Google Ads) - O segredo para o Google aparecer!
    y1: {
      type: 'linear',
      display: true,
      position: 'right',
      beginAtZero: true,
      grid: { display: false }, // Não polui o gráfico com mais linhas de grade
      ticks: { color: "#C5A059", font: { size: 9, weight: 'bold' } }
    }
  },
  elements: {
    line: { tension: 0.4, borderWidth: 3 },
    point: { radius: 0, hoverRadius: 6 }
  }
};

const styledData = computed(() => {
  if (!props.chartData.datasets) return props.chartData;
  return {
    ...props.chartData,
    datasets: props.chartData.datasets.map((dataset) => {
      const isMeta = dataset.label.toLowerCase().includes('meta');
      return {
        ...dataset,
        // Atribui o Google ao eixo y1 e a Meta ao eixo y
        yAxisID: isMeta ? 'y' : 'y1', 
        borderColor: isMeta ? '#1877F2' : '#C5A059',
        backgroundColor: isMeta ? 'rgba(24, 119, 242, 0.1)' : 'rgba(197, 160, 89, 0.1)',
        fill: true
      };
    })
  };
});
</script>

<template>
  <div class="relative w-full h-full p-4">
    <Line 
      v-if="styledData?.labels?.length > 0" 
      :data="styledData" 
      :options="options" 
    />
  </div>
</template>